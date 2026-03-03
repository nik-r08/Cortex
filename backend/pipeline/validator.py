import logging

logger = logging.getLogger(__name__)

# minimum confidence to accept an extraction
CONFIDENCE_THRESHOLD = 0.3


def validate_extractions(extractions: dict, doc_type: str) -> tuple[dict, list[str]]:
    """
    Check extracted fields for obvious problems.
    Returns (validated_fields, list_of_warnings).
    """
    validated = {}
    warnings = []

    for field, value in extractions.items():
        # skip None values
        if value is None:
            warnings.append(f"Field '{field}' is null, skipping")
            continue

        # check for suspiciously short values that might be garbage
        if isinstance(value, str) and len(value.strip()) == 0:
            warnings.append(f"Field '{field}' is empty string, skipping")
            continue

        validated[field] = value

    # type specific checks
    if doc_type == "invoice":
        if "total_amount" in validated:
            try:
                amt = str(validated["total_amount"]).replace(",", "").replace("$", "")
                float(amt)
            except ValueError:
                warnings.append(f"total_amount doesn't look like a number: {validated['total_amount']}")

    if doc_type == "resume":
        if "email" in validated:
            email = str(validated["email"])
            if "@" not in email:
                warnings.append(f"email doesn't look valid: {email}")

    if len(warnings) > 0:
        logger.info(f"Validation warnings for {doc_type}: {warnings}")

    return validated, warnings
