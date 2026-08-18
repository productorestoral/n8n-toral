import { INodeProperties } from 'n8n-workflow';

export const resourceOperations: INodeProperties[] = [
	{
		displayName: 'Resource',
		name: 'resource',
		type: 'options',
		noDataExpression: true,
		options: [
			{
				name: 'Gmail RAG',
				value: 'gmailRag',
			},
		],
		default: 'gmailRag',
	},
];

export const gmailRagOperations: INodeProperties[] = [
	{
		displayName: 'Operation',
		name: 'operation',
		type: 'options',
		noDataExpression: true,
		displayOptions: {
			show: {
				resource: ['gmailRag'],
			},
		},
		options: [
			{
				name: 'Search and Respond',
				value: 'searchAndRespond',
				description: 'Search in documents and generate response based on email query',
				action: 'Search and respond to email',
			},
			{
				name: 'Index Documents',
				value: 'indexDocuments',
				description: 'Index documents from Google Drive for RAG',
				action: 'Index documents',
			},
		],
		default: 'searchAndRespond',
	},
];

export const gmailRagFields: INodeProperties[] = [
	{
		displayName: 'Operation',
		name: 'operation',
		type: 'hidden',
		default: 'searchAndRespond',
	},
	// Search and Respond fields
	{
		displayName: 'Email ID',
		name: 'emailId',
		type: 'string',
		required: true,
		default: '',
		displayOptions: {
			show: {
				operation: ['searchAndRespond'],
			},
		},
		description: 'The Gmail email ID to process',
	},
	{
		displayName: 'Query Text',
		name: 'queryText',
		type: 'string',
		required: true,
		default: '',
		displayOptions: {
			show: {
				operation: ['searchAndRespond'],
			},
		},
		description: 'The query text to search documents for (or leave empty to extract from email)',
	},
	{
		displayName: 'Search Folder Name',
		name: 'searchFolderName',
		type: 'string',
		default: '',
		displayOptions: {
			show: {
				operation: ['searchAndRespond'],
			},
		},
		description: 'Optional folder name in Drive to search in (e.g., "Documentos_Seguros")',
	},
	{
		displayName: 'Top K Results',
		name: 'topK',
		type: 'number',
		default: 3,
		displayOptions: {
			show: {
				operation: ['searchAndRespond'],
			},
		},
		description: 'Number of top relevant documents to use for context',
	},
	{
		displayName: 'Custom Prompt Context',
		name: 'customPromptContext',
		type: 'string',
		typeOptions: {
			rows: 4,
		},
		default: '',
		displayOptions: {
			show: {
				operation: ['searchAndRespond'],
			},
		},
		description: 'Additional context or instructions for Gemini (e.g., "You are an insurance advisor for Productores Toral")',
	},
	{
		displayName: 'Include Source Documents',
		name: 'includeSources',
		type: 'boolean',
		default: true,
		displayOptions: {
			show: {
				operation: ['searchAndRespond'],
			},
		},
		description: 'Whether to include source documents in the response',
	},
	// Index Documents fields
	{
		displayName: 'Folder Name Pattern',
		name: 'folderNamePattern',
		type: 'string',
		default: '',
		displayOptions: {
			show: {
				operation: ['indexDocuments'],
			},
		},
		description: 'Optional pattern to filter documents by folder name',
	},
	{
		displayName: 'Rebuild Index',
		name: 'rebuildIndex',
		type: 'boolean',
		default: false,
		displayOptions: {
			show: {
				operation: ['indexDocuments'],
			},
		},
		description: 'Whether to rebuild the entire index (regenerate all embeddings)',
	},
];

export const description: INodeProperties[] = [...resourceOperations, ...gmailRagOperations, ...gmailRagFields];
