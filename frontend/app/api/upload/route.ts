import { NextRequest, NextResponse } from 'next/server';
import { BlobServiceClient, ContainerClient } from '@azure/storage-blob';
import { v4 as uuidv4 } from 'uuid';

// Helper function to ensure container exists
async function ensureContainerExists(blobServiceClient: BlobServiceClient, containerName: string): Promise<void> {
  try {
    const containerClient = blobServiceClient.getContainerClient(containerName);
    const exists = await containerClient.exists();
    
    if (!exists) {
      console.log(`Creating container ${containerName}`);
      await containerClient.create({ access: 'blob' });
      console.log(`Container ${containerName} created successfully`);
    } else {
      console.log(`Container ${containerName} already exists`);
    }
  } catch (error) {
    console.error(`Error creating container ${containerName}:`, error);
    throw error;
  }
}

// Helper function to check if blob exists
async function checkIfBlobExists(containerClient: ContainerClient, blobName: string): Promise<boolean> {
  try {
    const blobClient = containerClient.getBlobClient(blobName);
    const exists = await blobClient.exists();
    return exists;
  } catch (error) {
    return false;
  }
}

// POST: Upload a file to Azure Blob Storage
export async function POST(req: NextRequest) {
  try {
    // Process the form data
    const formData = await req.formData();
    const file = formData.get('file') as File;
    const projectId = formData.get('projectId') as string || 'default';
    const isTranscript = formData.get('isTranscript') === 'true';

    if (!file) {
      return NextResponse.json({ error: 'No file provided' }, { status: 400 });
    }

    // Get Azure Storage configuration from environment
    const accountName = process.env.AZURE_STORAGE_ACCOUNT_NAME;
    const accountKey = process.env.AZURE_STORAGE_ACCOUNT_KEY;
    const containerName = process.env.AZURE_STORAGE_CONTAINER_NAME || 'hipaadocs';
    
    if (!accountName || !accountKey) {
      console.error('Missing required Azure Storage environment variables');
      return NextResponse.json(
        { error: 'Storage configuration error' },
        { status: 500 }
      );
    }

    // Create connection string
    const connectionString = `DefaultEndpointsProtocol=https;AccountName=${accountName};AccountKey=${accountKey};EndpointSuffix=core.windows.net`;
    
    // Create the blob service client
    const blobServiceClient = BlobServiceClient.fromConnectionString(connectionString);
    
    try {
      // Ensure container exists
      await ensureContainerExists(blobServiceClient, containerName);
      
      // Get container client
      const containerClient = blobServiceClient.getContainerClient(containerName);
      
      // Create a unique blob name by adding a timestamp prefix to the original filename
      const timestamp = new Date().toISOString().replace(/[-:]/g, '').replace(/\..+/g, '');
      const uniqueId = uuidv4().substring(0, 8); // Take first 8 chars of a UUID for brevity
      const blobName = `${timestamp}_${uniqueId}_${file.name}`;
      
      // Create blob client with the unique name
      const blockBlobClient = containerClient.getBlockBlobClient(blobName);
      
      // Upload the file
      const fileSizeMB = (file.size / (1024 * 1024)).toFixed(2);
      console.log(`Uploading ${file.name} (${fileSizeMB} MB) to container ${containerName}`);
      const startTime = Date.now();
      
      // Convert file to ArrayBuffer
      const arrayBuffer = await file.arrayBuffer();
      
      // Upload the file with content type and metadata
      const uploadResponse = await blockBlobClient.uploadData(arrayBuffer, {
        blobHTTPHeaders: {
          blobContentType: file.type || 'application/pdf'
        },
        metadata: {
          projectId: projectId,
          isTranscript: isTranscript ? 'true' : 'false'
        }
      });
      
      // Calculate upload stats
      const elapsedTime = (Date.now() - startTime) / 1000;
      const uploadSpeed = file.size / (1024 * 1024 * elapsedTime);
      console.log(`Successfully uploaded ${blobName} in ${elapsedTime.toFixed(2)} seconds (${uploadSpeed.toFixed(2)} MB/s)`);
      
      // Get the URL to the blob
      const blobUrl = blockBlobClient.url;
      
      // Get the ETag from the upload response (remove quotes if present)
      const etag = uploadResponse.etag?.replace(/"/g, '') || '';
      
      // Return success response
      return NextResponse.json({ 
        success: true,
        id: etag,
        documentId: etag,
        filename: file.name,
        blobUrl: blobUrl,
        blobName: blobName,
        fileSize: file.size,
        projectId: projectId,
        isTranscript: isTranscript,
        uploadDate: new Date().toISOString(),
        status: 'processing',
        summary: null,
        extractedText: null,
        elapsedTime: elapsedTime,
        uploadSpeed: uploadSpeed
      }, { status: 201 });
    } catch (azureError) {
      console.error('Azure blob storage error:', azureError);
      throw azureError;
    }
  } catch (error) {
    console.error('Error uploading file:', error);
    return NextResponse.json(
      { error: 'Failed to upload file', details: error instanceof Error ? error.message : String(error) },
      { status: 500 }
    );
  }
} 