import {
	IDataObject,
	IExecuteFunctions,
	IHttpRequestMethods,
	INodeExecutionData,
} from 'n8n-workflow';
import { RAGDocument, RAGSearchResult, EmbeddingResult, GoogleFile, RAGResponse } from './types';

export async function googleApiRequest(
	this: IExecuteFunctions,
	method: IHttpRequestMethods,
	endpoint: string,
	body: IDataObject = {},
	qs: IDataObject = {},
	uri?: string,
	option: IDataObject = {},
): Promise<any> {
	const options = {
		headers: {
			'Content-Type': 'application/json',
		},
		method,
		body,
		qs,
		uri: uri || `https://www.googleapis.com${endpoint}`,
		json: true,
	};

	if (Object.keys(body).length === 0) {
		delete options.body;
	}

	Object.assign(options, option);

	return await this.helpers.requestWithAuthentication('googleApi', options);
}

export async function getGoogleDriveFiles(
	this: IExecuteFunctions,
	folderName?: string,
): Promise<GoogleFile[]> {
	let query = "trashed=false and (mimeType='text/plain' or mimeType='text/markdown')";

	if (folderName) {
		query += ` and name contains '${folderName}'`;
	}

	const response = await googleApiRequest.call(
		this,
		'GET',
		'/drive/v3/files',
		{},
		{
			q: query,
			spaces: 'drive',
			fields: 'files(id,name,mimeType,webContentLink,webViewLink)',
			pageSize: 100,
		},
	);

	return response.files || [];
}

export async function readGoogleDriveFile(this: IExecuteFunctions, fileId: string): Promise<string> {
	const response = await googleApiRequest.call(
		this,
		'GET',
		`/drive/v3/files/${fileId}`,
		{},
		{
			alt: 'media',
		},
		`https://www.googleapis.com/drive/v3/files/${fileId}?alt=media`,
	);

	if (typeof response === 'string') {
		return response;
	}

	return JSON.stringify(response);
}

export async function generateEmbedding(
	this: IExecuteFunctions,
	text: string,
	apiKey: string,
): Promise<number[]> {
	const options = {
		method: 'POST' as IHttpRequestMethods,
		url: 'https://generativelanguage.googleapis.com/v1beta/models/embedding-001:embedContent',
		headers: {
			'Content-Type': 'application/json',
		},
		qs: {
			key: apiKey,
		},
		json: true,
		body: {
			model: 'models/embedding-001',
			content: {
				parts: [
					{
						text: text,
					},
				],
			},
		},
	};

	try {
		const response = await this.helpers.request(options);
		return response.embedding?.values || [];
	} catch (error) {
		throw new Error(`Failed to generate embedding: ${error.message}`);
	}
}

export async function queryGemini(
	this: IExecuteFunctions,
	prompt: string,
	apiKey: string,
	context?: string,
): Promise<string> {
	const fullPrompt = context ? `${context}\n\nPregunta: ${prompt}` : prompt;

	const options = {
		method: 'POST' as IHttpRequestMethods,
		url: 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent',
		headers: {
			'Content-Type': 'application/json',
		},
		qs: {
			key: apiKey,
		},
		json: true,
		body: {
			contents: [
				{
					parts: [
						{
							text: fullPrompt,
						},
					],
				},
			],
			generationConfig: {
				temperature: 0.7,
				topK: 40,
				topP: 0.95,
				maxOutputTokens: 2048,
			},
			safetySettings: [
				{
					category: 'HARM_CATEGORY_SEXUALLY_EXPLICIT',
					threshold: 'BLOCK_MEDIUM_AND_ABOVE',
				},
				{
					category: 'HARM_CATEGORY_HATE_SPEECH',
					threshold: 'BLOCK_MEDIUM_AND_ABOVE',
				},
			],
		},
	};

	try {
		const response = await this.helpers.request(options);
		if (
			response.candidates &&
			response.candidates[0] &&
			response.candidates[0].content &&
			response.candidates[0].content.parts
		) {
			return response.candidates[0].content.parts[0].text;
		}
		throw new Error('No response from Gemini');
	} catch (error) {
		throw new Error(`Failed to query Gemini: ${error.message}`);
	}
}

export function cosineSimilarity(a: number[], b: number[]): number {
	let dotProduct = 0;
	let normA = 0;
	let normB = 0;

	for (let i = 0; i < a.length; i++) {
		dotProduct += a[i] * b[i];
		normA += a[i] * a[i];
		normB += b[i] * b[i];
	}

	if (normA === 0 || normB === 0) {
		return 0;
	}

	return dotProduct / (Math.sqrt(normA) * Math.sqrt(normB));
}

export function searchDocuments(
	documents: RAGDocument[],
	queryEmbedding: number[],
	topK: number = 3,
): RAGSearchResult[] {
	const results = documents
		.map((doc) => ({
			documentId: doc.id,
			fileName: doc.fileName,
			relevanceScore: doc.embedding ? cosineSimilarity(queryEmbedding, doc.embedding) : 0,
			snippet: doc.content.substring(0, 500),
		}))
		.sort((a, b) => b.relevanceScore - a.relevanceScore)
		.slice(0, topK);

	return results;
}

export function extractTextFromPayload(payload: any): string {
	let text = '';

	if (payload.parts) {
		for (const part of payload.parts) {
			if (part.mimeType.startsWith('text/')) {
				if (part.body?.data) {
					text += Buffer.from(part.body.data, 'base64').toString('utf-8');
				}
			}
		}
	} else if (payload.body?.data) {
		text = Buffer.from(payload.body.data, 'base64').toString('utf-8');
	}

	return text;
}

export function getEmailSubject(headers: any[]): string {
	if (!headers) return '';
	const subjectHeader = headers.find((h: any) => h.name.toLowerCase() === 'subject');
	return subjectHeader?.value || '';
}

export function getEmailFrom(headers: any[]): string {
	if (!headers) return '';
	const fromHeader = headers.find((h: any) => h.name.toLowerCase() === 'from');
	return fromHeader?.value || '';
}
