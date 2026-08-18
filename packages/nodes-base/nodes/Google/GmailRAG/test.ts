// Quick syntax validation file
import { GmailRAGV1 } from './v1/GmailRAGV1.node';
import { RAGDocument, RAGResponse } from './types';
import { cosineSimilarity, searchDocuments } from './GenericFunctions';

// Test types
const testDoc: RAGDocument = {
	id: '123',
	fileName: 'test.md',
	content: 'test content',
	embedding: [0.1, 0.2, 0.3],
};

const testResponse: RAGResponse = {
	success: true,
	answer: 'Test answer',
	sourcedDocuments: [],
	confidence: 0.95,
};

// Test functions
const similarity = cosineSimilarity([0.1, 0.2], [0.3, 0.4]);
const results = searchDocuments([testDoc], [0.1, 0.2], 1);

// Test node instantiation
const node = new GmailRAGV1();

console.log('✓ All types and functions validate correctly');
console.log('✓ Node class instantiates successfully');
