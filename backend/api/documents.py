import logging
import uuid
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models.document import Document
from backend.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/documents", tags=["documents"])

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_TYPES = {
    "application/pdf",
    "text/plain",
    "text/csv",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, f"Unsupported file type: {file.content_type}")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(400, "File too large, max 10MB")

    file_id = str(uuid.uuid4())
    ext = Path(file.filename).suffix if file.filename else ".bin"
    file_path = UPLOAD_DIR / f"{file_id}{ext}"
    file_path.write_bytes(content)

    doc = Document(
        filename=file.filename or "untitled",
        file_path=str(file_path),
        file_size=len(content),
        mime_type=file.content_type,
        status="pending",
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)

    logger.info(f"Uploaded document {doc.id}: {doc.filename}")
    return {"id": str(doc.id), "status": doc.status, "filename": doc.filename}
