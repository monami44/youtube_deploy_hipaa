/**
 * API service for communicating with the backend
 */

// When running in Docker, the backend service is available at "http://backend:8000"
// For local development, fallback to "http://localhost:8080"
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://backend:8000';

console.log("Using API URL:", API_URL);

/**
 * Determines if code is running on the server or client
 */
const isServer = typeof window === 'undefined';

/**
 * Gets the appropriate base URL for API requests
 * - Server-side: use direct backend URL
 * - Client-side: use local proxy
 */
function getBaseUrl(path: string): string {
  // For server-side requests, use the direct backend URL
  if (isServer) {
    return `${API_URL}/api/${path}`;
  }
  
  // For client-side requests, use our Next.js API proxy
  return `/api/proxy/${path}`;
}

export interface Document {
  id: string;
  filename: string;
  uploadDate: string;
  status: string;
  summary: string | null;
  extractedText: string | null;
  blobUrl?: string;
  blobName?: string;
  fileSize?: number;
}

/**
 * Fetch all documents
 */
export async function getDocuments(): Promise<Document[]> {
  const url = getBaseUrl('documents');
  console.log(`Making API request to: ${url}`);
  
  const response = await fetch(url);
  
  if (!response.ok) {
    console.error(`API request failed with status: ${response.status}`);
    throw new Error('Failed to fetch documents');
  }
  
  const data = await response.json();
  console.log(`API returned ${data.length} documents`);
  
  // Transform the data to match our frontend model
  const documents = data.map(transformDocumentFromBackend);
  return documents;
}

/**
 * Get a specific document by ID
 */
export async function getDocument(id: string): Promise<Document> {
  const url = getBaseUrl(`documents/${id}`);
  console.log(`Making API request to: ${url}`);
  
  const response = await fetch(url);
  
  if (!response.ok) {
    console.error(`API request failed with status: ${response.status}`);
    throw new Error('Failed to fetch document');
  }
  
  const data = await response.json();
  // Transform the data to match our frontend model
  return transformDocumentFromBackend(data);
}

/**
 * Upload a document to Azure storage
 */
export async function uploadDocument(file: File, isTranscript: boolean = false): Promise<Document> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('isTranscript', isTranscript ? 'true' : 'false');
  
  const response = await fetch('/api/upload', {
    method: 'POST',
    body: formData,
  });
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.error || 'Failed to upload document');
  }
  
  return response.json();
}

/**
 * Regenerate a document summary with a custom prompt
 */
export async function regenerateSummary(documentId: string, prompt: string): Promise<{ summary: string }> {
  const url = getBaseUrl(`documents/${documentId}/regenerate-summary`);
  console.log(`Making regenerate summary request to: ${url}`, { documentId, prompt });
  
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ custom_prompt: prompt }),
  });
  
  if (!response.ok) {
    const errorText = await response.text().catch(() => 'Unknown error');
    console.error(`Failed to regenerate summary: ${response.status}`, errorText);
    throw new Error(`Failed to regenerate summary: ${response.status}`);
  }
  
  const result = await response.json();
  console.log('Summary regenerated successfully:', result);
  return result;
}

/**
 * Transform document from backend format to frontend format
 */
function transformDocumentFromBackend(doc: any): Document {
  // Log the raw document to see its structure
  console.log('Raw document from backend:', doc);
  
  return {
    id: doc.id,
    filename: doc.original_filename || doc.filename || 'Unnamed Document',
    uploadDate: doc.created_at || doc.uploadDate || new Date().toISOString(),
    status: doc.status || 'unknown',
    summary: doc.summary,
    extractedText: doc.extracted_text || doc.extractedText,
    blobUrl: doc.blob_url || doc.blobUrl,
    blobName: doc.blob_name || doc.blobName,
    fileSize: doc.file_size || doc.fileSize
  };
} 