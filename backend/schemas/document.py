from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from backend.models.document import DocumentStatus, DocumentType


class DocumentUploadResponse(BaseModel):
    id: UUID
    filename: str
    content_type: str
    file_size: int
    status: DocumentStatus
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentResponse(BaseModel):
    id: UUID
    filename: str
    original_filename: str
    content_type: str
    file_size: int
    status: DocumentStatus
    document_type: Optional[DocumentType] = None
    classification_confidence: Optional[float] = None
    page_count: Optional[int] = None
    metadata_: Optional[dict] = Field(None, alias="metadata_")
    error_message: Optional[str] = None
    retry_count: int = 0
    created_at: datetime
    updated_at: datetime
    processed_at: Optional[datetime] = None

    model_config = {"from_attributes": True, "populate_by_name": True}


class DocumentListResponse(BaseModel):
    documents: list[DocumentResponse]
    total: int
    page: int
    page_size: int
    has_next: bool


class DocumentFilterParams(BaseModel):
    status: Optional[DocumentStatus] = None
    document_type: Optional[DocumentType] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
