import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from backend.database import Base


class JobStage(str, enum.Enum):
    PARSING = "parsing"
    CLASSIFICATION = "classification"
    EXTRACTION = "extraction"
    VALIDATION = "validation"


class JobStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


class ProcessingJob(Base):
    __tablename__ = "processing_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )

    stage = Column(Enum(JobStage), nullable=False)
    status = Column(Enum(JobStatus), nullable=False, default=JobStatus.PENDING)

    worker_id = Column(String(100), nullable=True)
    attempt = Column(Float, default=1)
    duration_ms = Column(Float, nullable=True)

    result = Column(JSONB, nullable=True)
    error_message = Column(Text, nullable=True)

    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    document = relationship("Document", back_populates="processing_jobs")

    def __repr__(self):
        return f"<Job {self.stage}:{self.status} doc={self.document_id}>"
