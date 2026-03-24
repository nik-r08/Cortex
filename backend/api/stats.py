from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models.document import Document, DocumentStatus
from backend.models.processing_job import ProcessingJob, JobStatus
from backend.schemas.job import ProcessingStatsResponse

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/", response_model=ProcessingStatsResponse)
async def get_stats(db: AsyncSession = Depends(get_db)):
    # total count
    total = (await db.execute(select(func.count(Document.id)))).scalar() or 0

    # count by status
    status_q = (
        select(Document.status, func.count(Document.id))
        .group_by(Document.status)
    )
    status_rows = (await db.execute(status_q)).all()
    by_status = {s.value: c for s, c in status_rows}

    completed = by_status.get("completed", 0)
    failed = by_status.get("failed", 0)
    in_progress = total - completed - failed

    # count by document type
    type_q = (
        select(Document.document_type, func.count(Document.id))
        .where(Document.document_type.isnot(None))
        .group_by(Document.document_type)
    )
    type_rows = (await db.execute(type_q)).all()
    by_type = {t.value: c for t, c in type_rows}

    # avg processing time from completed jobs
    avg_q = (
        select(func.avg(ProcessingJob.duration_ms))
        .where(ProcessingJob.status == JobStatus.COMPLETED)
    )
    avg_time = (await db.execute(avg_q)).scalar()

    return ProcessingStatsResponse(
        total_documents=total,
        completed=completed,
        failed=failed,
        in_progress=in_progress,
        avg_processing_time_ms=round(avg_time, 2) if avg_time else None,
        documents_by_type=by_type,
        documents_by_status=by_status,
    )
