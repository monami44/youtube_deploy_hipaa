from sqlalchemy import Column, Integer, String, Text, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.db.database import Base

class Document(Base):
    """Model for storing document information"""
    
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    blob_url = Column(String, nullable=False)
    content_type = Column(String, nullable=False)
    status = Column(String, nullable=False, default="pending")  # pending, processing, completed, error
    extracted_text = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Document(id={self.id}, filename={self.filename}, status={self.status})>" 