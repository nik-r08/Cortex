# Cortex

AI document processing pipeline. Work in progress.

## Idea

Build a system that takes unstructured documents (PDFs, invoices, contracts) and extracts structured data using LLMs. Think of it as an intelligent OCR replacement.

## Planned Stack
- Python (FastAPI) for the API
- Celery + Redis for async processing
- PostgreSQL for storage
- Gemini or Groq for the LLM layer
- React for the dashboard

## Setup

```bash
cp .env.example .env
docker-compose up --build
```

API at http://localhost:8000/docs
