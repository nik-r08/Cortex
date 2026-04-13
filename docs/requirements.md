# Project Requirements

## MVP Scope
- Upload PDF or text file via API
- Classify document type using LLM
- Extract key fields based on type
- Store results in postgres
- Full text search across documents
- Basic dashboard for uploading and viewing

## Document Types (MVP)
- Invoice: number, vendor, date, total, line items
- Resume: name, email, skills, experience, education
- Contract: parties, dates, value, key terms
- Report: title, author, summary, findings
- Other: best effort extraction

## Non Goals (for now)
- OCR for scanned documents
- Multi user / auth
- Real time processing (async is fine)
- Batch upload (do one at a time first)

## Deployment

Target: Render (free tier) + Neon (free postgres)
Redis: Render managed Redis or Upstash

See README for deploy instructions.
