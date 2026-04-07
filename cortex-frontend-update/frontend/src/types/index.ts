export interface Document {
  id: string
  filename: string
  original_filename: string
  content_type: string
  file_size: number
  file_path: string
  status: string
  document_type: string | null
  content_text: string | null
  created_at: string
  updated_at: string
}

export interface Extraction {
  id: string
  document_id: string
  field_name: string
  field_value: string
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
  duration_ms: number | null
  error_message: string | null
  created_at: string
}

export type DocumentStatus = 'uploaded' | 'parsing' | 'classifying' | 'extracting' | 'validating' | 'completed' | 'failed'
export type DocumentType = 'invoice' | 'resume' | 'contract' | 'report' | 'other'
