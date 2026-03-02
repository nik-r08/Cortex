CLASSIFICATION_PROMPT = """Analyze the following document text and classify it into one of these categories:
invoice, resume, contract, report, form, letter, other

Document text:
---
{text}
---

Return a JSON object with:
- "type": one of the categories above
- "confidence": a number between 0 and 1 indicating how confident you are
"""

# extraction prompts per document type
EXTRACTION_PROMPTS = {
    "invoice": """Extract the following fields from this invoice:
- invoice_number
- vendor_name
- vendor_address
- date
- due_date
- subtotal
- tax
- total_amount
- currency
- line_items (as a list of objects with description, quantity, unit_price, amount)

Document text:
---
{text}
---

Return a JSON object with these fields. Use null for fields you cannot find.""",

    "resume": """Extract the following fields from this resume:
- full_name
- email
- phone
- location
- summary (1 sentence)
- skills (list of strings)
- experience (list of objects with company, title, start_date, end_date)
- education (list of objects with institution, degree, field, year)

Document text:
---
{text}
---

Return a JSON object with these fields. Use null for fields you cannot find.""",

    "contract": """Extract the following fields from this contract:
- contract_type
- parties (list of party names)
- effective_date
- expiration_date
- total_value
- currency
- key_terms (list of important terms or clauses, max 5)
- governing_law

Document text:
---
{text}
---

Return a JSON object with these fields. Use null for fields you cannot find.""",

    "report": """Extract the following fields from this report:
- title
- author
- date
- organization
- summary (2 sentences max)
- key_findings (list of strings, max 5)

Document text:
---
{text}
---

Return a JSON object with these fields. Use null for fields you cannot find.""",

    "default": """Extract any structured information you can find in this document.
Look for names, dates, amounts, addresses, key terms, and other notable data.

Document text:
---
{text}
---

Return a JSON object where keys are descriptive field names and values are the extracted data.""",
}


def get_extraction_prompt(doc_type: str, text: str) -> str:
    template = EXTRACTION_PROMPTS.get(doc_type, EXTRACTION_PROMPTS["default"])
    return template.format(text=text[:8000])  # cap the text length for token limits

# contract prompts still need work, keeping it simple for now
