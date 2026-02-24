import logging
from celery import Celery
from backend.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

celery_app = Celery("cortex", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

@celery_app.task(bind=True, max_retries=3, default_retry_delay=10)
def process_document(self, document_id: str):
    """Main pipeline task. Stages will be added here."""
    logger.info(f"Processing document {document_id}")
    # TODO: implement pipeline stages
    pass
