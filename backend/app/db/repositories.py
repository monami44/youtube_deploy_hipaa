from sqlalchemy.orm import Session
import uuid
from app.models.document import Document

class DocumentRepository:
    """Repository for document database operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_document(self, filename, original_filename, blob_url, content_type):
        """Create a new document
        
        Args:
            filename: The name of the file in blob storage
            original_filename: The original name of the file
            blob_url: The URL of the blob
            content_type: The content type of the file
            
        Returns:
            The created document
        """
        document = Document(
            filename=filename,
            original_filename=original_filename,
            blob_url=blob_url,
            content_type=content_type,
            status="pending"
        )
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document
    
    def get_document_by_id(self, document_id):
        """Get a document by ID
        
        Args:
            document_id: The ID of the document
            
        Returns:
            The document or None if not found
        """
        return self.db.query(Document).filter(Document.id == document_id).first()
    
    def get_document_by_filename(self, filename):
        """Get a document by filename
        
        Args:
            filename: The filename to search for
            
        Returns:
            The document or None if not found
        """
        return self.db.query(Document).filter(Document.filename == filename).first()
    
    def get_all_documents(self):
        """Get all documents
        
        Returns:
            A list of all documents
        """
        return self.db.query(Document).order_by(Document.created_at.desc()).all()
    
    def get_pending_documents(self):
        """Get all pending documents
        
        Returns:
            A list of pending documents
        """
        return self.db.query(Document).filter(Document.status == "pending").all()
    
    def update_document_status(self, document_id, status):
        """Update the status of a document
        
        Args:
            document_id: The ID of the document
            status: The new status
            
        Returns:
            The updated document or None if not found
        """
        document = self.get_document_by_id(document_id)
        if document:
            document.status = status
            self.db.commit()
            self.db.refresh(document)
        return document
    
    def update_document_text_and_summary(self, document_id, extracted_text, summary):
        """Update the extracted text and summary of a document
        
        Args:
            document_id: The ID of the document
            extracted_text: The extracted text
            summary: The summary
            
        Returns:
            The updated document or None if not found
        """
        document = self.get_document_by_id(document_id)
        if document:
            document.extracted_text = extracted_text
            document.summary = summary
            document.status = "completed"
            self.db.commit()
            self.db.refresh(document)
        return document
    
    def update_document_summary(self, document_id, summary):
        """Update the summary of a document
        
        Args:
            document_id: The ID of the document
            summary: The new summary
            
        Returns:
            The updated document or None if not found
        """
        document = self.get_document_by_id(document_id)
        if document:
            document.summary = summary
            self.db.commit()
            self.db.refresh(document)
        return document 