from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uuid
import os
from typing import List, Optional

from app.db.database import get_db, engine, Base
from app.db.repositories import DocumentRepository
from app.models.document import Document
from app.utils.azure_storage import azure_storage_client
from app.utils.document_intelligence import document_intelligence_service
from app.utils.summarizer import document_summarizer

# Initialize FastAPI app
app = FastAPI(
    title="Document Processing Service",
    description="HIPAA compliant document processing service",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, specify exact domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Document model for API responses
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class DocumentResponse(BaseModel):
    id: UUID
    original_filename: str
    status: str
    created_at: datetime
    updated_at: datetime
    summary: Optional[str] = None
    
    class Config:
        orm_mode = True

class SummaryRequest(BaseModel):
    custom_prompt: str

@app.get("/api/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok"}

@app.post("/api/documents", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    is_transcript: Optional[bool] = Form(False),
    db: Session = Depends(get_db)
):
    """Upload a document to the service"""
    try:
        # Ensure file is a PDF
        if not file.content_type or "pdf" not in file.content_type.lower():
            raise HTTPException(status_code=400, detail="Only PDF files are accepted")
        
        # Generate a unique filename
        filename = f"{uuid.uuid4()}.pdf"
        file_content = await file.read()
        
        # Prepare metadata
        metadata = {
            "isTranscript": str(is_transcript).lower()
        }
        
        # Upload file to Azure Blob Storage with metadata
        upload_result = azure_storage_client.upload_file(
            file_content, 
            filename, 
            file.content_type,
            metadata=metadata
        )
        
        # Create document in database
        repo = DocumentRepository(db)
        document = repo.create_document(
            filename=filename,
            original_filename=file.filename,
            blob_url=upload_result['url'],
            content_type=file.content_type
        )
        
        return document
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/documents", response_model=List[DocumentResponse])
def get_documents(db: Session = Depends(get_db)):
    """Get all documents"""
    repo = DocumentRepository(db)
    documents = repo.get_all_documents()
    return documents

@app.get("/api/documents/{document_id}", response_model=DocumentResponse)
def get_document(document_id: UUID, db: Session = Depends(get_db)):
    """Get a document by ID"""
    repo = DocumentRepository(db)
    document = repo.get_document_by_id(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

@app.post("/api/documents/{document_id}/regenerate-summary", response_model=DocumentResponse)
def regenerate_summary(
    document_id: UUID, 
    summary_request: SummaryRequest,
    db: Session = Depends(get_db)
):
    """Regenerate the summary for a document using a custom prompt"""
    repo = DocumentRepository(db)
    document = repo.get_document_by_id(document_id)
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if not document.extracted_text:
        raise HTTPException(status_code=400, detail="Document has not been processed yet")
    
    # Generate new summary with custom prompt
    new_summary = document_summarizer.generate_summary(
        document.extracted_text,
        custom_prompt=summary_request.custom_prompt
    )
    
    # Update document with new summary
    updated_document = repo.update_document_summary(document_id, new_summary)
    
    return updated_document

# Include worker routes for completeness
@app.get("/worker/health")
def worker_health_check():
    """Worker health check endpoint"""
    return {"status": "ok"} 