import os
import logging
from azure.storage.blob import BlobServiceClient, ContentSettings
from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class AzureStorageClient:
    """Client for Azure Blob Storage operations"""
    
    def __init__(self):
        """Initialize the Azure Storage client"""
        self.connection_string = settings.azure_storage_connection_string
        self.container_name = settings.azure_storage_container_name
        self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        self.container_client = self.blob_service_client.get_container_client(self.container_name)
        self._processed_blobs = set()  # Set to track processed blob etags
    
    def upload_file(self, file_content, filename, content_type, metadata=None):
        """Upload a file to Azure Blob Storage
        
        Args:
            file_content: The content of the file
            filename: The name of the file in Azure Blob Storage
            content_type: The content type of the file
            metadata: Optional metadata to attach to the blob
            
        Returns:
            The URL of the uploaded blob and its properties
        """
        # Create blob client
        blob_client = self.container_client.get_blob_client(filename)
        
        # Set content settings
        content_settings = ContentSettings(content_type=content_type)
        
        # Upload the file
        upload_response = blob_client.upload_blob(
            file_content, 
            content_settings=content_settings,
            metadata=metadata,
            overwrite=True
        )
        
        # Get blob properties including etag
        properties = blob_client.get_blob_properties()
        etag = properties.etag.strip('"') if properties.etag else None
        
        return {
            'url': blob_client.url,
            'etag': etag,
            'filename': filename,
            'content_type': content_type
        }
    
    def list_blobs(self):
        """List all blobs in the container
        
        Returns:
            A list of blob names
        """
        return [blob.name for blob in self.container_client.list_blobs()]
    
    def download_blob(self, blob_name):
        """Download a blob from the container
        
        Args:
            blob_name: The name of the blob to download
            
        Returns:
            The blob content
        """
        blob_client = self.container_client.get_blob_client(blob_name)
        return blob_client.download_blob().readall()
    
    def delete_blob(self, blob_name):
        """Delete a blob from the container
        
        Args:
            blob_name: The name of the blob to delete
        """
        blob_client = self.container_client.get_blob_client(blob_name)
        blob_client.delete_blob()
    
    def get_blob_properties(self, blob_name):
        """Get blob properties including ETag and metadata
        
        Args:
            blob_name: The name of the blob
            
        Returns:
            A dictionary of blob properties
        """
        try:
            blob_client = self.container_client.get_blob_client(blob_name)
            properties = blob_client.get_blob_properties()
            
            # Extract the ETag (remove quotes)
            etag = properties.etag.strip('"') if properties.etag else None
            
            # Get metadata
            metadata = {}
            if hasattr(properties, "metadata") and properties.metadata:
                metadata = properties.metadata
            
            return {
                "etag": etag,
                "filename": blob_name,
                "content_type": properties.content_settings.content_type,
                "size": properties.size,
                "blob_url": blob_client.url,
                "metadata": metadata
            }
        except Exception as e:
            logger.error(f"Error getting blob properties for {blob_name}: {str(e)}")
            return None
    
    def find_unprocessed_blobs(self, processed_etags=None):
        """Find all PDF blobs that haven't been processed yet
        
        Args:
            processed_etags: Optional set of already processed blob etags
            
        Returns:
            A list of dictionaries with blob properties
        """
        result = []
        
        # If no processed etags provided, use the internal tracking set
        if processed_etags is None:
            processed_etags = self._processed_blobs
        
        try:
            # List all blobs in the container
            for blob in self.container_client.list_blobs():
                # Only process PDF files
                if blob.name.lower().endswith('.pdf'):
                    # Get blob properties
                    properties = self.get_blob_properties(blob.name)
                    if not properties:
                        continue
                    
                    etag = properties.get('etag')
                    if not etag:
                        continue
                    
                    # Skip if already processed
                    if etag in processed_etags:
                        continue
                    
                    logger.info(f"Found unprocessed PDF: {blob.name} (etag: {etag})")
                    result.append(properties)
            
            return result
        except Exception as e:
            logger.error(f"Error finding unprocessed blobs: {str(e)}")
            return []
    
    def mark_as_processed(self, etag):
        """Mark a blob as processed using its ETag
        
        Args:
            etag: The ETag of the processed blob
        """
        if etag:
            self._processed_blobs.add(etag)
            logger.info(f"Marked blob with etag {etag} as processed")

# Create a singleton instance
azure_storage_client = AzureStorageClient() 