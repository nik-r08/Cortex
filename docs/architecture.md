# Cortex Architecture

## Pipeline Flow

Upload -> Parse -> Classify -> Extract -> Validate -> Store -> Search

## Components

1. Upload API: accepts PDFs and text files
2. Parser: extracts raw text from documents
3. Classifier: LLM determines document type (invoice, resume, contract, etc)
4. Extractor: LLM pulls structured fields based on document type
5. Validator: checks extraction quality, flags low confidence
6. Storage: PostgreSQL with full text search
7. Dashboard: React UI for uploads and browsing

## Why async?

Document processing takes 5-15 seconds per doc (LLM API calls).
Can't block the API server. Use Celery workers + Redis queue.

## Data Model

Documents -> has many Extractions
Documents -> has many ProcessingJobs (one per pipeline stage)
