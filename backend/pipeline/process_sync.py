"""
Synchronous (inline) document processing for environments without Celery/Redis.
Called directly from the upload endpoint in a background task.
"""
import json
import logging
from datetime import datetime

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import get_settings
from backend.models.document import Document, DocumentStatus, DocumentType
from backend.models.extraction import Extraction
from backend.models.processing_job import ProcessingJob, JobStage, JobStatus

logger = logging.getLogger(__name__)
settings = get_settings()


def get_llm_provider():
    if settings.llm_provider == "groq" and settings.groq_api_key:
        from backend.llm.groq import GroqProvider
        return GroqProvider(settings.groq_api_key)
    elif settings.gemini_api_key:
        from backend.llm.gemini import GeminiProvider
        return GeminiProvider(settings.gemini_api_key)
    else:
        raise RuntimeError("No LLM provider configured")


async def create_job(db: AsyncSession, doc_id, stage: JobStage) -> ProcessingJob:
    job = ProcessingJob(
        document_id=doc_id,
        stage=stage,
        status=JobStatus.RUNNING,
        started_at=datetime.utcnow(),
    )
    db.add(job)
    await db.flush()
    return job


async def complete_job(db: AsyncSession, job: ProcessingJob):
    job.status = JobStatus.COMPLETED
    job.completed_at = datetime.utcnow()
    if job.started_at:
        job.duration_ms = (job.completed_at - job.started_at).total_seconds() * 1000
    await db.flush()


async def fail_job(db: AsyncSession, job: ProcessingJob, error: str):
    job.status = JobStatus.FAILED
    job.completed_at = datetime.utcnow()
    job.error_message = error
    if job.started_at:
        job.duration_ms = (job.completed_at - job.started_at).total_seconds() * 1000
    await db.flush()


async def process_document_inline(document_id: str):
    """Run the full pipeline inline using async db sessions."""
    from backend.database import async_session

    async with async_session() as db:
        try:
            from sqlalchemy import select
            result = await db.execute(
                select(Document).where(Document.id == document_id)
            )
            doc = result.scalar_one_or_none()
            if not doc:
                logger.error(f"Document {document_id} not found")
                return

            llm = get_llm_provider()

            # STAGE 1: parse
            doc.status = DocumentStatus.CLASSIFYING
            await db.flush()

            job = await create_job(db, doc.id, JobStage.PARSING)
            try:
                from backend.pipeline.parser import extract_text
                raw_text, page_count = extract_text(doc.file_path, doc.content_type)
                doc.raw_text = raw_text
                doc.page_count = page_count
                await db.flush()
                await complete_job(db, job)
            except Exception as e:
                await fail_job(db, job, str(e))
                doc.status = DocumentStatus.FAILED
                doc.error_message = f"Parsing failed: {e}"
                await db.commit()
                return

            if not doc.raw_text:
                doc.status = DocumentStatus.FAILED
                doc.error_message = "No text could be extracted"
                await db.commit()
                return

            # STAGE 2: classify
            doc.status = DocumentStatus.CLASSIFYING
            await db.flush()

            job = await create_job(db, doc.id, JobStage.CLASSIFICATION)
            try:
                from backend.pipeline.classifier import classify_document
                doc_type, confidence = await classify_document(doc.raw_text, llm)
                doc.document_type = DocumentType(doc_type)
                doc.classification_confidence = confidence
                doc.status = DocumentStatus.EXTRACTING
                await db.flush()
                await complete_job(db, job)
            except Exception as e:
                await fail_job(db, job, str(e))
                doc.status = DocumentStatus.FAILED
                doc.error_message = f"Classification failed: {e}"
                await db.commit()
                return

            # STAGE 3: extract
            job = await create_job(db, doc.id, JobStage.EXTRACTION)
            try:
                from backend.pipeline.extractor import extract_fields, compute_field_confidence
                fields = await extract_fields(doc.raw_text, doc_type, llm)

                for field_name, field_value in fields.items():
                    conf = compute_field_confidence(field_value)
                    ext = Extraction(
                        document_id=doc.id,
                        field_name=field_name,
                        field_value=json.dumps(field_value) if not isinstance(field_value, str) else field_value,
                        field_type=type(field_value).__name__ if field_value else "null",
                        confidence=conf,
                        method="llm",
                        raw_response=fields,
                    )
                    db.add(ext)

                doc.status = DocumentStatus.VALIDATING
                await db.flush()
                await complete_job(db, job)
            except Exception as e:
                await fail_job(db, job, str(e))
                doc.status = DocumentStatus.FAILED
                doc.error_message = f"Extraction failed: {e}"
                await db.commit()
                return

            # STAGE 4: validate
            job = await create_job(db, doc.id, JobStage.VALIDATION)
            try:
                from backend.pipeline.validator import validate_extractions
                validated, warnings = validate_extractions(fields, doc_type)

                search_text = f"{doc.original_filename} {doc.raw_text[:2000]}"
                for v in validated.values():
                    if isinstance(v, str):
                        search_text += f" {v}"

                await db.execute(
                    text(
                        "UPDATE documents SET search_vector = to_tsvector('english', :txt) WHERE id = :id"
                    ),
                    {"txt": search_text[:10000], "id": str(doc.id)},
                )

                doc.status = DocumentStatus.COMPLETED
                doc.processed_at = datetime.utcnow()
                await db.flush()
                await complete_job(db, job)
            except Exception as e:
                await fail_job(db, job, str(e))
                doc.status = DocumentStatus.FAILED
                doc.error_message = f"Validation failed: {e}"
                await db.commit()
                return

            await db.commit()
            logger.info(f"Document {document_id} processed successfully")

        except Exception as e:
            logger.exception(f"Unexpected error processing {document_id}: {e}")
            try:
                doc.status = DocumentStatus.FAILED
                doc.error_message = str(e)
                await db.commit()
            except:
                pass
