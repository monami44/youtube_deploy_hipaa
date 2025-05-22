import time
import asyncio
import logging
from sqlalchemy.orm import Session
import traceback
import os
from pathlib import Path
import tempfile
import uuid

from app.core.config import settings
from app.db.database import SessionLocal
from app.db.repositories import DocumentRepository
from app.utils.azure_storage import azure_storage_client
from app.utils.document_intelligence import document_intelligence_service
from app.utils.summarizer import document_summarizer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

class DocumentProcessingWorker:
    """Worker for processing documents in the background"""
    
    def __init__(self):
        """Initialize the worker"""
        self.poll_interval = settings.poll_interval_seconds
        # Track processed document ETags
        self.processed_etags = set()
        logger.info(f"Worker initialized with poll interval: {self.poll_interval} seconds")
    
    def get_db(self):
        """Get a database session"""
        db = SessionLocal()
        try:
            return db
        finally:
            db.close()
    
    async def process_document(self, document, db: Session):
        """Process a document from the database
        
        Args:
            document: The document to process
            db: Database session
        """
        try:
            # Update document status
            repo = DocumentRepository(db)
            repo.update_document_status(document.id, "processing")
            logger.info(f"Processing document: {document.id}")
            
            # Download document from blob storage
            blob_content = azure_storage_client.download_blob(document.filename)
            
            # Extract text using Document Intelligence
            extracted_text = document_intelligence_service.analyze_document(blob_content)
            logger.info(f"Text extracted from document: {document.id}")
            
            # Generate summary
            summary = document_summarizer.generate_summary(extracted_text)
            logger.info(f"Summary generated for document: {document.id}")
            
            # Update document with extracted text and summary
            repo.update_document_text_and_summary(document.id, extracted_text, summary)
            logger.info(f"Document processing completed: {document.id}")
            
        except Exception as e:
            logger.error(f"Error processing document {document.id}: {str(e)}")
            logger.error(traceback.format_exc())
            repo.update_document_status(document.id, "error")
    
    async def process_blob_document(self, blob_properties, temp_file_path=None):
        """Process a document directly from blob storage
        
        Args:
            blob_properties: The properties of the blob to process
            temp_file_path: Optional path to temporary file
        """
        db = None
        try:
            # Get database session
            db = self.get_db()
            repo = DocumentRepository(db)
            
            # Extract properties
            etag = blob_properties.get('etag')
            filename = blob_properties.get('filename')
            blob_url = blob_properties.get('blob_url')
            content_type = blob_properties.get('content_type')
            
            # Create document record in database
            original_filename = os.path.basename(filename)
            document = repo.create_document(filename, original_filename, blob_url, content_type)
            logger.info(f"Created document record: {document.id} for blob: {filename} (etag: {etag})")
            
            # Update document status
            repo.update_document_status(document.id, "processing")
            
            # Process document content
            if temp_file_path:
                # If we have a temp file, read it
                with open(temp_file_path, 'rb') as f:
                    blob_content = f.read()
            else:
                # Otherwise download from blob storage
                blob_content = azure_storage_client.download_blob(filename)
            
            # Extract text using Document Intelligence
            extracted_text = document_intelligence_service.analyze_document(blob_content)
            logger.info(f"Text extracted from document: {document.id}")
            
            # Generate summary
            summary = document_summarizer.generate_summary(extracted_text)
            logger.info(f"Summary generated for document: {document.id}")
            
            # Update document with extracted text and summary
            repo.update_document_text_and_summary(document.id, extracted_text, summary)
            logger.info(f"Document processing completed: {document.id}")
            
            # Mark the blob as processed
            azure_storage_client.mark_as_processed(etag)
            self.processed_etags.add(etag)
            
            return document
            
        except Exception as e:
            logger.error(f"Error processing blob document: {str(e)}")
            logger.error(traceback.format_exc())
            if db:
                try:
                    # Try to update document status if it was created
                    repo = DocumentRepository(db)
                    # Try to find the document by filename if we have it
                    if 'filename' in blob_properties:
                        document = repo.get_document_by_filename(blob_properties['filename'])
                        if document:
                            repo.update_document_status(document.id, "error")
                except Exception:
                    pass
        finally:
            if db:
                db.close()
            
            # Clean up temporary file if it exists
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                    logger.info(f"Cleaned up temporary file: {temp_file_path}")
                except Exception as e:
                    logger.error(f"Error cleaning up temporary file: {str(e)}")
    
    async def download_blob_to_temp(self, blob_name):
        """Download a blob to a temporary file
        
        Args:
            blob_name: Name of the blob to download
            
        Returns:
            Path to the temporary file
        """
        try:
            # Create temp directory if it doesn't exist
            temp_dir = Path(tempfile.gettempdir()) / "docprocessor"
            temp_dir.mkdir(exist_ok=True)
            
            # Generate a unique temp file name
            temp_file = temp_dir / f"{uuid.uuid4()}_{os.path.basename(blob_name)}"
            
            # Download the blob
            blob_content = azure_storage_client.download_blob(blob_name)
            
            # Write to temp file
            with open(temp_file, 'wb') as f:
                f.write(blob_content)
                
            logger.info(f"Downloaded blob {blob_name} to {temp_file}")
            return temp_file
        except Exception as e:
            logger.error(f"Error downloading blob to temp file: {str(e)}")
            return None
    
    async def load_processed_documents(self):
        """Load already processed document etags from the database"""
        try:
            db = self.get_db()
            # Query all documents and get their filenames
            documents = db.query(Document).all()
            
            # For each document, get the blob properties and extract the etag
            for document in documents:
                try:
                    properties = azure_storage_client.get_blob_properties(document.filename)
                    if properties and 'etag' in properties:
                        etag = properties['etag']
                        if etag:
                            self.processed_etags.add(etag)
                except Exception:
                    # If we can't get properties, just continue
                    pass
                    
            logger.info(f"Loaded {len(self.processed_etags)} processed document etags")
        except Exception as e:
            logger.error(f"Error loading processed documents: {str(e)}")
        finally:
            db.close()
            
    async def poll_for_new_blobs(self):
        """Poll Azure Blob Storage for new documents and process them"""
        await self.load_processed_documents()
        
        while True:
            try:
                logger.info("Polling for new blobs in Azure Storage...")
                
                # Find unprocessed blobs
                unprocessed_blobs = azure_storage_client.find_unprocessed_blobs(self.processed_etags)
                
                if unprocessed_blobs:
                    logger.info(f"Found {len(unprocessed_blobs)} new documents to process")
                    
                    # Process each new document
                    for blob_properties in unprocessed_blobs:
                        try:
                            # Get the filename
                            filename = blob_properties.get('filename')
                            
                            # Download to temp file
                            temp_file = await self.download_blob_to_temp(filename)
                            
                            # Process the document
                            if temp_file:
                                await self.process_blob_document(blob_properties, temp_file)
                            else:
                                # Try processing without temp file
                                await self.process_blob_document(blob_properties)
                                
                        except Exception as e:
                            logger.error(f"Error processing blob: {str(e)}")
                            # Mark as processed anyway to avoid retry loops
                            etag = blob_properties.get('etag')
                            if etag:
                                azure_storage_client.mark_as_processed(etag)
                                self.processed_etags.add(etag)
                else:
                    logger.info("No new blobs found")
                
                # Wait before polling again
                await asyncio.sleep(self.poll_interval)
                
            except Exception as e:
                logger.error(f"Error in blob polling loop: {str(e)}")
                logger.error(traceback.format_exc())
                await asyncio.sleep(self.poll_interval)
    
    async def poll_pending_documents(self):
        """Poll for pending documents in the database and process them"""
        while True:
            try:
                # Get database session
                db = self.get_db()
                
                # Get pending documents
                repo = DocumentRepository(db)
                pending_documents = repo.get_pending_documents()
                
                if pending_documents:
                    logger.info(f"Found {len(pending_documents)} pending documents in database")
                    
                    # Process each document
                    for document in pending_documents:
                        await self.process_document(document, db)
                
                # Wait before polling again
                await asyncio.sleep(self.poll_interval)
                
            except Exception as e:
                logger.error(f"Error in database poll loop: {str(e)}")
                logger.error(traceback.format_exc())
                await asyncio.sleep(self.poll_interval)
            finally:
                db.close()

# Import for loading processed documents
from app.models.document import Document

# Main function to run the worker
async def run_worker():
    """Run the document processing worker"""
    logger.info("Starting document processing worker")
    worker = DocumentProcessingWorker()
    
    # Start tasks to poll both the database and blob storage
    task1 = asyncio.create_task(worker.poll_pending_documents())
    task2 = asyncio.create_task(worker.poll_for_new_blobs())
    
    # Wait for both tasks (they should run indefinitely)
    await asyncio.gather(task1, task2)

# Start the worker when script is run directly
if __name__ == "__main__":
    asyncio.run(run_worker()) 