from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from backend.models.processing_job import JobStage, JobStatus


class ProcessingJobResponse(BaseModel):
    id: UUID
    document_id: UUID
    stage: JobStage
    status: JobStatus
    attempt: float
    duration_ms: Optional[float] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class PipelineStatusResponse(BaseModel):
    document_id: UUID
    document_status: str
    jobs: list[ProcessingJobResponse]
    total_duration_ms: Optional[float] = None


class ProcessingStatsResponse(BaseModel):
    total_documents: int
    completed: int
    failed: int
    in_progress: int
    avg_processing_time_ms: Optional[float] = None
    documents_by_type: dict[str, int]
    documents_by_status: dict[str, int]
