from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class ExtractionResponse(BaseModel):
    id: UUID
    document_id: UUID
    field_name: str
    field_value: Optional[str] = None
    field_type: str
    confidence: float
    method: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ExtractionSummary(BaseModel):
    document_id: UUID
    document_type: Optional[str] = None
    total_fields: int
    avg_confidence: float
    extractions: list[ExtractionResponse]
# aggregate extraction results by field for overview
