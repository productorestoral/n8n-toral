import {
	IDataObject,
	IExecuteFunctions,
	INodeExecutionData,
	INodeType,
	INodeTypeDescription,
	NodeOperationError,
} from 'n8n-workflow';

import { description } from '../DescriptionFile';
import {
	googleApiRequest,
	getGoogleDriveFiles,
	readGoogleDriveFile,
	generateEmbedding,
	queryGemini,
	searchDocuments,
	extractTextFromPayload,
	getEmailSubject,
	getEmailFrom,
} from '../GenericFunctions';
import { RAGDocument, RAGResponse, GoogleFile } from '../types';

export class GmailRAGV1 implements INodeType {
	description: INodeTypeDescription = {
		displayName: 'Gmail RAG',
		name: 'gmailRag',
		icon: 'file:gmail.svg',
		group: ['transform'],
		version: 1,
		description: 'Search documents and generate responses to emails using RAG',
		defaults: {
			name: 'Gmail RAG',
		},
		inputs: ['main'],
		outputs: ['main'],
		credentials: [
			{
				name: 'googleApi',
				required: true,
			},
		],
		properties: description,
	};

	async execute(this: IExecuteFunctions): Promise<INodeExecutionData[][]> {
		const items = this.getInputData();
		const returnData: INodeExecutionData[] = [];
		const resource = this.getNodeParameter('resource', 0) as string;
		const operation = this.getNodeParameter('operation', 0) as string;

		// Get Google API credentials
		const credentials = await this.getCredentials('googleApi');
		if (!credentials) {
			throw new NodeOperationError(this.getNode(), 'No credentials configured');
		}

		const apiKey = credentials.apiKey as string;

		if (resource === 'gmailRag') {
			if (operation === 'searchAndRespond') {
				for (let i = 0; i < items.length; i++) {
					try {
						const result = await this.searchAndRespond(this, i, apiKey);
						returnData.push({
							json: result,
							pairedItem: i,
						});
					} catch (error) {
						if (this.continueOnFail()) {
							returnData.push({
								json: {
									error: error.message,
									success: false,
								},
								pairedItem: i,
							});
						} else {
							throw error;
						}
					}
				}
			} else if (operation === 'indexDocuments') {
				for (let i = 0; i < items.length; i++) {
					try {
						const result = await this.indexDocuments(this, apiKey);
						returnData.push({
							json: result,
							pairedItem: i,
						});
					} catch (error) {
						if (this.continueOnFail()) {
							returnData.push({
								json: {
									error: error.message,
									success: false,
									indexed: 0,
								},
								pairedItem: i,
							});
						} else {
							throw error;
						}
					}
				}
			}
		}

		return [returnData];
	}

	private async searchAndRespond(
		context: IExecuteFunctions,
		itemIndex: number,
		apiKey: string,
	): Promise<RAGResponse> {
		// Get parameters
		const emailId = context.getNodeParameter('emailId', itemIndex) as string;
		let queryText = context.getNodeParameter('queryText', itemIndex) as string;
		const searchFolderName = context.getNodeParameter('searchFolderName', itemIndex) as string;
		const topK = context.getNodeParameter('topK', itemIndex) as number;
		const customPromptContext = context.getNodeParameter('customPromptContext', itemIndex) as string;
		const includeSources = context.getNodeParameter('includeSources', itemIndex) as boolean;

		// Get email content
		const emailResponse = await googleApiRequest.call(
			context,
			'GET',
			`/gmail/v1/users/me/messages/${emailId}`,
			{},
			{
				format: 'full',
			},
		);

		// Extract email text and subject
		const emailText = extractTextFromPayload(emailResponse.payload);
		const emailSubject = getEmailSubject(emailResponse.payload?.headers);
		const emailFrom = getEmailFrom(emailResponse.payload?.headers);

		// Use email text as query if not provided
		if (!queryText) {
			queryText = emailSubject || emailText.substring(0, 500);
		}

		// Get documents from Drive
		const files = await getGoogleDriveFiles.call(context, searchFolderName);

		if (files.length === 0) {
			return {
				success: false,
				answer: 'No documents found in Drive to search.',
				sourcedDocuments: [],
				confidence: 0,
				error: 'No documents found',
			};
		}

		// Load and process documents
		const documents: RAGDocument[] = [];
		for (const file of files) {
			try {
				const content = await readGoogleDriveFile.call(context, file.id);
				documents.push({
					id: file.id,
					fileName: file.name,
					content,
				});
			} catch (error) {
				console.warn(`Failed to read document ${file.name}:`, error.message);
			}
		}

		if (documents.length === 0) {
			return {
				success: false,
				answer: 'Could not load documents from Drive.',
				sourcedDocuments: [],
				confidence: 0,
				error: 'Failed to load documents',
			};
		}

		// Generate embedding for query
		const queryEmbedding = await generateEmbedding.call(context, queryText, apiKey);

		// Generate embeddings for documents (in parallel chunks)
		const batchSize = 5;
		for (let i = 0; i < documents.length; i += batchSize) {
			const batch = documents.slice(i, Math.min(i + batchSize, documents.length));
			await Promise.all(
				batch.map(async (doc) => {
					try {
						doc.embedding = await generateEmbedding.call(context, doc.content, apiKey);
					} catch (error) {
						console.warn(`Failed to generate embedding for ${doc.fileName}:`, error.message);
					}
				}),
			);
		}

		// Search documents
		const searchResults = searchDocuments(documents, queryEmbedding, topK);

		if (searchResults.length === 0) {
			return {
				success: false,
				answer: 'No relevant documents found for your query.',
				sourcedDocuments: [],
				confidence: 0,
			};
		}

		// Build context from documents
		const context_text = searchResults
			.map((result) => {
				const doc = documents.find((d) => d.id === result.documentId);
				return `[${result.fileName}]\n${doc?.content}`;
			})
			.join('\n\n---\n\n');

		// Create prompt for Gemini
		const systemPrompt = customPromptContext
			? customPromptContext
			: `Eres un asesor de seguros profesional para Productores Toral. Responde de manera clara, concisa y profesional.
Basate ÚNICAMENTE en los documentos proporcionados. Si la información no está en los documentos, indica que no puedes responder.`;

		const fullPrompt = `${systemPrompt}

DOCUMENTOS DE REFERENCIA:
${context_text}

PREGUNTA DEL CLIENTE:
${queryText}

RESPUESTA:`;

		// Query Gemini
		const answer = await queryGemini.call(context, fullPrompt, apiKey);

		return {
			success: true,
			answer,
			sourcedDocuments: includeSources ? searchResults : [],
			confidence: searchResults[0]?.relevanceScore || 0,
		};
	}

	private async indexDocuments(context: IExecuteFunctions, apiKey: string): Promise<IDataObject> {
		// Get parameters
		const folderNamePattern = context.getNodeParameter('folderNamePattern', 0) as string;
		const rebuildIndex = context.getNodeParameter('rebuildIndex', 0) as boolean;

		// Get documents from Drive
		const files = await getGoogleDriveFiles.call(context, folderNamePattern);

		if (files.length === 0) {
			return {
				success: false,
				indexed: 0,
				message: 'No documents found in Drive',
			};
		}

		// Load documents
		const documents: RAGDocument[] = [];
		for (const file of files) {
			try {
				const content = await readGoogleDriveFile.call(context, file.id);
				documents.push({
					id: file.id,
					fileName: file.name,
					content,
				});
			} catch (error) {
				console.warn(`Failed to read document ${file.name}:`, error.message);
			}
		}

		// Generate embeddings
		let indexed = 0;
		const batchSize = 5;
		for (let i = 0; i < documents.length; i += batchSize) {
			const batch = documents.slice(i, Math.min(i + batchSize, documents.length));
			await Promise.all(
				batch.map(async (doc) => {
					try {
						doc.embedding = await generateEmbedding.call(context, doc.content, apiKey);
						indexed++;
					} catch (error) {
						console.warn(`Failed to generate embedding for ${doc.fileName}:`, error.message);
					}
				}),
			);
		}

		// TODO: Save embeddings to persistent storage (could use n8n's data storage or external DB)

		return {
			success: true,
			indexed,
			total: documents.length,
			message: `Successfully indexed ${indexed} documents`,
		};
	}
}
