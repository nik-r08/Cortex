import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Column, DateTime, Enum, Float, Index,
    Integer, String, Text, func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID, TSVECTOR
from sqlalchemy.orm import relationship

from backend.database import Base


class DocumentStatus(str, enum.Enum):
    UPLOADED = "uploaded"
    CLASSIFYING = "classifying"
    EXTRACTING = "extracting"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"


class DocumentType(str, enum.Enum):
    INVOICE = "invoice"
    RESUME = "resume"
    CONTRACT = "contract"
    REPORT = "report"
    FORM = "form"
    LETTER = "letter"
    OTHER = "other"


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String(500), nullable=False)
    original_filename = Column(String(500), nullable=False)
    content_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_path = Column(String(1000), nullable=False)

    # processing state
    status = Column(
        Enum(DocumentStatus), nullable=False,
        default=DocumentStatus.UPLOADED, index=True,
    )
    document_type = Column(Enum(DocumentType), nullable=True, index=True)
    classification_confidence = Column(Float, nullable=True)

    raw_text = Column(Text, nullable=True)
    page_count = Column(Integer, nullable=True)
    metadata_ = Column("metadata", JSONB, nullable=True, default=dict)

    # postgres full text search
    search_vector = Column(TSVECTOR, nullable=True)

    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    processed_at = Column(DateTime, nullable=True)

    extractions = relationship(
        "Extraction", back_populates="document", cascade="all, delete-orphan"
    )
    processing_jobs = relationship(
        "ProcessingJob", back_populates="document", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_documents_search", "search_vector", postgresql_using="gin"),
        Index("ix_documents_created", "created_at"),
        Index("ix_documents_status_type", "status", "document_type"),
    )

    def __repr__(self):
        return f"<Document {self.id} ({self.filename}) [{self.status}]>"
# GIN index on content and extracted_data for fast search
