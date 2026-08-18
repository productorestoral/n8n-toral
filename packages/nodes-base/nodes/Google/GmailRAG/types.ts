export interface GoogleFile {
	id: string;
	name: string;
	mimeType: string;
	webContentLink?: string;
	webViewLink?: string;
}

export interface RAGDocument {
	id: string;
	fileName: string;
	content: string;
	embedding?: number[];
}

export interface RAGSearchResult {
	documentId: string;
	fileName: string;
	relevanceScore: number;
	snippet: string;
}

export interface GoogleEmailMessage {
	id: string;
	threadId: string;
	labelIds: string[];
	snippet: string;
	payload?: {
		headers?: Array<{
			name: string;
			value: string;
		}>;
		body?: {
			data?: string;
		};
		parts?: Array<{
			headers?: Array<{
				name: string;
				value: string;
			}>;
			body?: {
				data?: string;
			};
		}>;
	};
}

export interface RAGResponse {
	success: boolean;
	answer: string;
	sourcedDocuments: RAGSearchResult[];
	confidence: number;
	error?: string;
}

export interface EmbeddingResult {
	documentId: string;
	fileName: string;
	embedding: number[];
}
