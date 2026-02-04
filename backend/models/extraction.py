import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from backend.database import Base


class Extraction(Base):
    __tablename__ = "extractions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )

    field_name = Column(String(200), nullable=False)
    field_value = Column(Text, nullable=True)
    field_type = Column(String(50), nullable=False, default="string")

    confidence = Column(Float, nullable=False, default=0.0)
    method = Column(String(50), nullable=False, default="llm")

    # keep the raw llm output around for debugging
    raw_response = Column(JSONB, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    document = relationship("Document", back_populates="extractions")

    def __repr__(self):
        return f"<Extraction {self.field_name}={self.field_value}>"
