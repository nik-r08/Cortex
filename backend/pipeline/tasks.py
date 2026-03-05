"""
Celery tasks for the document processing pipeline.

Flow: parse -> classify -> extract -> validate -> done
Each step updates the document status and creates a ProcessingJob record.
"""
import json
import logging
import time
from datetime import datetime

from celery import Celery
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from backend.config import get_settings
from backend.models.document import Document, DocumentStatus, DocumentType
from backend.models.extraction import Extraction
from backend.models.processing_job import ProcessingJob, JobStage, JobStatus

logger = logging.getLogger(__name__)
settings = get_settings()

# celery needs a sync engine since it runs outside the async event loop
celery_app = Celery("cortex", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

sync_engine = create_engine(settings.database_url_sync)
SyncSession = sessionmaker(bind=sync_engine)


def get_llm_provider():
    """Build the right LLM provider based on config."""
    # we have to do a lazy import here to avoid circular deps
    # and also because we need to run async stuff from sync celery
    if settings.llm_provider == "groq" and settings.groq_api_key:
        from backend.llm.groq import GroqProvider
        return GroqProvider(settings.groq_api_key)
    elif settings.gemini_api_key:
        from backend.llm.gemini import GeminiProvider
        return GeminiProvider(settings.gemini_api_key)
    else:
        raise RuntimeError("No LLM provider configured. Set GEMINI_API_KEY or GROQ_API_KEY")


def create_job(db: Session, doc_id, stage: JobStage) -> ProcessingJob:
    job = ProcessingJob(
        document_id=doc_id,
        stage=stage,
        status=JobStatus.RUNNING,
        started_at=datetime.utcnow(),
    )
    db.add(job)
    db.commit()
    return job


def complete_job(db: Session, job: ProcessingJob, result=None):
    job.status = JobStatus.COMPLETED
    job.completed_at = datetime.utcnow()
    if job.started_at:
        job.duration_ms = (job.completed_at - job.started_at).total_seconds() * 1000
    job.result = result
    db.commit()


def fail_job(db: Session, job: ProcessingJob, error: str):
    job.status = JobStatus.FAILED
    job.completed_at = datetime.utcnow()
    job.error_message = error
    if job.started_at:
        job.duration_ms = (job.completed_at - job.started_at).total_seconds() * 1000
    db.commit()


@celery_app.task(bind=True, max_retries=3, default_retry_delay=10)
def process_document(self, document_id: str):
    """
    Main pipeline task. Runs all stages sequentially.
    Could split these into separate chained tasks later for better
    observability, but keeping it simple for now.
    """
    import asyncio

    db = SyncSession()
    try:
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            logger.error(f"Document {document_id} not found")
            return

        llm = get_llm_provider()
        loop = asyncio.new_event_loop()

        # STAGE 1: parse
        doc.status = DocumentStatus.CLASSIFYING
        db.commit()

        job = create_job(db, doc.id, JobStage.PARSING)
        try:
            from backend.pipeline.parser import extract_text
            raw_text, page_count = extract_text(doc.file_path, doc.content_type)
            doc.raw_text = raw_text
            doc.page_count = page_count
            db.commit()
            complete_job(db, job, {"page_count": page_count, "text_length": len(raw_text)})
        except Exception as e:
            fail_job(db, job, str(e))
            doc.status = DocumentStatus.FAILED
            doc.error_message = f"Parsing failed: {e}"
            db.commit()
            return

        if not doc.raw_text:
            doc.status = DocumentStatus.FAILED
            doc.error_message = "No text could be extracted from document"
            db.commit()
            return

        # STAGE 2: classify
        job = create_job(db, doc.id, JobStage.CLASSIFICATION)
        try:
            from backend.pipeline.classifier import classify_document
            doc_type, confidence = loop.run_until_complete(
                classify_document(doc.raw_text, llm)
            )
            doc.document_type = DocumentType(doc_type)
            doc.classification_confidence = confidence
            doc.status = DocumentStatus.EXTRACTING
            db.commit()
            complete_job(db, job, {"type": doc_type, "confidence": confidence})
        except Exception as e:
            fail_job(db, job, str(e))
            doc.status = DocumentStatus.FAILED
            doc.error_message = f"Classification failed: {e}"
            db.commit()
            return

        # STAGE 3: extract
        job = create_job(db, doc.id, JobStage.EXTRACTION)
        try:
            from backend.pipeline.extractor import extract_fields, compute_field_confidence
            fields = loop.run_until_complete(
                extract_fields(doc.raw_text, doc_type, llm)
            )

            # save each field as an Extraction record
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
            db.commit()
            complete_job(db, job, {"fields_extracted": len(fields)})
        except Exception as e:
            fail_job(db, job, str(e))
            doc.status = DocumentStatus.FAILED
            doc.error_message = f"Extraction failed: {e}"
            db.commit()
            return

        # STAGE 4: validate
        job = create_job(db, doc.id, JobStage.VALIDATION)
        try:
            from backend.pipeline.validator import validate_extractions
            validated, warnings = validate_extractions(fields, doc_type)

            # update search vector for full text search
            search_text = f"{doc.original_filename} {doc.raw_text[:2000]}"
            for v in validated.values():
                if isinstance(v, str):
                    search_text += f" {v}"
            db.execute(
                text(
                    "UPDATE documents SET search_vector = to_tsvector('english', :txt) WHERE id = :id"
                ),
                {"txt": search_text[:10000], "id": str(doc.id)},
            )

            doc.status = DocumentStatus.COMPLETED
            doc.processed_at = datetime.utcnow()
            db.commit()
            complete_job(db, job, {"warnings": warnings, "validated_fields": len(validated)})
        except Exception as e:
            fail_job(db, job, str(e))
            doc.status = DocumentStatus.FAILED
            doc.error_message = f"Validation failed: {e}"
            db.commit()
            return

        loop.close()
        logger.info(f"Document {document_id} processed successfully")

    except Exception as e:
        logger.exception(f"Unexpected error processing {document_id}: {e}")
        try:
            doc = db.query(Document).filter(Document.id == document_id).first()
            if doc:
                doc.status = DocumentStatus.FAILED
                doc.error_message = f"Unexpected error: {e}"
                doc.retry_count += 1
                db.commit()
        except:
            pass

        # retry the task if we haven't exceeded max retries
        raise self.retry(exc=e)
    finally:
        db.close()
