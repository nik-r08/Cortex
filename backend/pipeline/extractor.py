import logging

from backend.llm.base import LLMProvider
from backend.llm.prompts import get_extraction_prompt

logger = logging.getLogger(__name__)


async def extract_fields(text: str, doc_type: str, llm: LLMProvider) -> dict:
    """
    Use the LLM to pull structured fields out of the document.
    Returns a dict of field_name -> field_value.
    """
    if not text.strip():
        return {}

    prompt = get_extraction_prompt(doc_type, text)

    try:
        result = await llm.generate_json(prompt)
        if not isinstance(result, dict):
            logger.warning(f"Extraction returned non-dict: {type(result)}")
            return {}
        return result
    except (ValueError, RuntimeError) as e:
        logger.error(f"Extraction failed for {doc_type}: {e}")
        return {}


def compute_field_confidence(value) -> float:
    """
    Simple heuristic for how much we trust an extracted value.
    None/empty -> 0, short strings -> lower, longer -> higher.
    """
    if value is None:
        return 0.0
    if isinstance(value, str):
        if not value.strip():
            return 0.0
        if len(value) < 3:
            return 0.5
        return 0.85
    if isinstance(value, (list, dict)):
        if len(value) == 0:
            return 0.1
        return 0.8
    # numbers, bools, etc
    return 0.9
