import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def extract_text_from_pdf(file_path: str) -> tuple[str, int]:
    """Pull text out of a PDF. Returns (text, page_count)."""
    try:
        import fitz  # PyMuPDF
    except ImportError:
        raise RuntimeError("PyMuPDF not installed. pip install PyMuPDF")

    doc = fitz.open(file_path)
    pages = []
    for page in doc:
        pages.append(page.get_text())
    doc.close()

    text = "\n\n".join(pages)
    return text.strip(), len(pages)


def extract_text_from_txt(file_path: str) -> tuple[str, int]:
    """Read a plain text file."""
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        text = f.read()
    # page count doesn't really apply to txt, just say 1
    return text.strip(), 1


def extract_text(file_path: str, content_type: str) -> tuple[str, int]:
    """Route to the right parser based on content type."""
    if content_type == "application/pdf":
        return extract_text_from_pdf(file_path)
    elif content_type == "text/plain":
        return extract_text_from_txt(file_path)
    elif content_type in ("image/png", "image/jpeg"):
        # TODO: OCR support, for now just return empty
        logger.warning(f"Image parsing not yet implemented for {file_path}")
        return "", 1
    else:
        logger.warning(f"Unknown content type: {content_type}")
        return "", 0
