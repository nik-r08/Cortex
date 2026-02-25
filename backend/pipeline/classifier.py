import logging

from backend.llm.base import LLMProvider
from backend.llm.prompts import CLASSIFICATION_PROMPT

logger = logging.getLogger(__name__)

VALID_TYPES = {"invoice", "resume", "contract", "report", "form", "letter", "other"}


async def classify_document(text: str, llm: LLMProvider) -> tuple[str, float]:
    """
    Ask the LLM to classify the document.
    Returns (document_type, confidence).
    Falls back to "other" if anything goes wrong.
    """
    if not text.strip():
        return "other", 0.0

    # only send the first ~4000 chars for classification, don't need the whole thing
    prompt = CLASSIFICATION_PROMPT.format(text=text[:4000])

    try:
        result = await llm.generate_json(prompt)
        doc_type = result.get("type", "other").lower().strip()
        confidence = float(result.get("confidence", 0.0))

        if doc_type not in VALID_TYPES:
            logger.warning(f"LLM returned unknown type '{doc_type}', defaulting to 'other'")
            doc_type = "other"

        confidence = max(0.0, min(1.0, confidence))
        return doc_type, confidence

    except (ValueError, RuntimeError) as e:
        logger.error(f"Classification failed: {e}")
        return "other", 0.0
