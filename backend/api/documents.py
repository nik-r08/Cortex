import os
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import get_settings
from backend.database import get_db
from backend.models.document import Document, DocumentStatus, DocumentType
from backend.models.extraction import Extraction
from backend.models.processing_job import ProcessingJob
from backend.schemas.document import (
    DocumentFilterParams,
    DocumentListResponse,
    DocumentResponse,
    DocumentUploadResponse,
)
from backend.schemas.extraction import ExtractionResponse, ExtractionSummary
from backend.schemas.job import PipelineStatusResponse, ProcessingJobResponse

router = APIRouter(prefix="/documents", tags=["documents"])
settings = get_settings()

ALLOWED_TYPES = {
    "application/pdf",
    "text/plain",
    "image/png",
    "image/jpeg",
}


async def save_upload(file: UploadFile) -> tuple[str, str, int]:
    """Save uploaded file to disk, return (saved_filename, path, size)."""
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    ext = Path(file.filename or "document").suffix
    saved_name = f"{uuid.uuid4().hex}{ext}"
    path = upload_dir / saved_name

    content = await file.read()
    file_size = len(content)

    if file_size > settings.max_file_size_bytes:
        raise HTTPException(413, f"File too large. Max {settings.max_file_size_mb}MB")

    with open(path, "wb") as f:
        f.write(content)

    return saved_name, str(path), file_size


@router.post("/", response_model=DocumentUploadResponse, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            400,
            f"Unsupported file type: {file.content_type}. "
            f"Allowed: {', '.join(ALLOWED_TYPES)}"
        )

    saved_name, path, size = await save_upload(file)

    doc = Document(
        filename=saved_name,
        original_filename=file.filename or "document",
        content_type=file.content_type or "application/octet-stream",
        file_size=size,
        file_path=path,
        status=DocumentStatus.UPLOADED,
    )
    db.add(doc)
    await db.flush()

    # TODO: trigger celery pipeline task here
    # process_document.delay(str(doc.id))

    return doc


@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    status: DocumentStatus | None = Query(None),
    document_type: DocumentType | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    query = select(Document)

    if status:
        query = query.where(Document.status == status)
    if document_type:
        query = query.where(Document.document_type == document_type)

    # get total count
    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    # paginate
    offset = (page - 1) * page_size
    query = query.order_by(Document.created_at.desc()).offset(offset).limit(page_size)
    result = await db.execute(query)
    docs = result.scalars().all()

    return DocumentListResponse(
        documents=[DocumentResponse.model_validate(d) for d in docs],
        total=total,
        page=page,
        page_size=page_size,
        has_next=(offset + page_size) < total,
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(404, "Document not found")
    return doc


@router.get("/{document_id}/extractions", response_model=ExtractionSummary)
async def get_extractions(document_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(404, "Document not found")

    ext_result = await db.execute(
        select(Extraction)
        .where(Extraction.document_id == document_id)
        .order_by(Extraction.field_name)
    )
    extractions = ext_result.scalars().all()

    avg_conf = 0.0
    if extractions:
        avg_conf = sum(e.confidence for e in extractions) / len(extractions)

    return ExtractionSummary(
        document_id=document_id,
        document_type=doc.document_type.value if doc.document_type else None,
        total_fields=len(extractions),
        avg_confidence=round(avg_conf, 3),
        extractions=[ExtractionResponse.model_validate(e) for e in extractions],
    )


@router.get("/{document_id}/status", response_model=PipelineStatusResponse)
async def get_pipeline_status(document_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(404, "Document not found")

    jobs_result = await db.execute(
        select(ProcessingJob)
        .where(ProcessingJob.document_id == document_id)
        .order_by(ProcessingJob.created_at)
    )
    jobs = jobs_result.scalars().all()

    total_ms = None
    if jobs:
        durations = [j.duration_ms for j in jobs if j.duration_ms is not None]
        if durations:
            total_ms = sum(durations)

    return PipelineStatusResponse(
        document_id=document_id,
        document_status=doc.status.value,
        jobs=[ProcessingJobResponse.model_validate(j) for j in jobs],
        total_duration_ms=total_ms,
    )


@router.delete("/{document_id}", status_code=204)
async def delete_document(document_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(404, "Document not found")

    # clean up the file on disk
    if doc.file_path and os.path.exists(doc.file_path):
        os.remove(doc.file_path)

    await db.delete(doc)
