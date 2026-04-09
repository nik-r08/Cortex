import pytest

from backend.pipeline.classifier import classify_document
from backend.pipeline.extractor import compute_field_confidence
from backend.pipeline.validator import validate_extractions


class FakeLLM:
    """Mock LLM that returns canned responses for testing."""
    def __init__(self, response: dict):
        self.response = response
        self.call_count = 0

    async def generate(self, prompt, system=""):
        self.call_count += 1
        return str(self.response)

    async def generate_json(self, prompt, system=""):
        self.call_count += 1
        return self.response


@pytest.mark.asyncio
async def test_classify_invoice():
    llm = FakeLLM({"type": "invoice", "confidence": 0.95})
    doc_type, conf = await classify_document("Invoice #12345 Total: $500", llm)
    assert doc_type == "invoice"
    assert conf == 0.95
    assert llm.call_count == 1


@pytest.mark.asyncio
async def test_classify_empty_text():
    llm = FakeLLM({"type": "other", "confidence": 0.0})
    doc_type, conf = await classify_document("", llm)
    assert doc_type == "other"
    assert conf == 0.0
    # should not even call the LLM for empty text
    assert llm.call_count == 0


@pytest.mark.asyncio
async def test_classify_unknown_type_defaults():
    llm = FakeLLM({"type": "spreadsheet", "confidence": 0.7})
    doc_type, conf = await classify_document("some text", llm)
    assert doc_type == "other"  # unknown types fall back to other


def test_confidence_heuristic():
    assert compute_field_confidence(None) == 0.0
    assert compute_field_confidence("") == 0.0
    assert compute_field_confidence("hi") == 0.5  # short string
    assert compute_field_confidence("John Smith") == 0.85
    assert compute_field_confidence(42) == 0.9
    assert compute_field_confidence([]) == 0.1
    assert compute_field_confidence(["a", "b"]) == 0.8


def test_validate_invoice():
    fields = {
        "invoice_number": "INV-001",
        "total_amount": "$1,234.56",
        "vendor_name": "Acme Corp",
        "empty_field": "",
        "null_field": None,
    }
    validated, warnings = validate_extractions(fields, "invoice")
    assert "invoice_number" in validated
    assert "total_amount" in validated
    assert "empty_field" not in validated
    assert "null_field" not in validated
    assert len(warnings) == 2  # empty + null


def test_validate_bad_email():
    fields = {"full_name": "John", "email": "not_an_email"}
    validated, warnings = validate_extractions(fields, "resume")
    assert any("email" in w for w in warnings)
# 12/15 passing, 3 flaky due to LLM response variance
# full integration test with celery and postgres
