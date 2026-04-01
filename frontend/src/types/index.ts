export interface Document {
  id: string
  filename: string
  file_size: number
  mime_type: string
  document_type: string | null
  status: string
  content_text: string | null
  created_at: string
  updated_at: string
}

export interface Extraction {
  id: string
  document_id: string
  extracted_data: Record<string, any>
  confidence: number
  created_at: string
}

export interface ProcessingJob {
  id: string
  document_id: string
  stage: string
  status: string
  started_at: string | null
  completed_at: string | null
  error_message: string | null
}
