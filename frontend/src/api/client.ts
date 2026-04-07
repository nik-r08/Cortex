import axios from 'axios'
import type { Document, Extraction, ProcessingJob } from '../types'

const api = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
})

// documents

export async function uploadDocument(file: File) {
  const form = new FormData()
  form.append('file', file)
  const res = await api.post('/documents/', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return res.data
}

interface ListParams {
  status?: string
  document_type?: string
  page?: number
  page_size?: number
}

export interface DocumentListResponse {
  documents: Document[]
  total: number
  page: number
  page_size: number
  has_next: boolean
}

export async function getDocuments(params?: ListParams): Promise<DocumentListResponse> {
  const res = await api.get('/documents/', { params })
  return res.data
}

export async function getDocument(id: string): Promise<Document> {
  const res = await api.get(`/documents/${id}`)
  return res.data
}

export async function deleteDocument(id: string) {
  await api.delete(`/documents/${id}`)
}

// extractions

export interface ExtractionSummary {
  document_id: string
  document_type: string | null
  total_fields: number
  avg_confidence: number
  extractions: Extraction[]
}

export async function getExtractions(docId: string): Promise<ExtractionSummary> {
  const res = await api.get(`/documents/${docId}/extractions`)
  return res.data
}

// pipeline status

export interface PipelineStatus {
  document_id: string
  document_status: string
  jobs: ProcessingJob[]
  total_duration_ms: number | null
}

export async function getPipelineStatus(docId: string): Promise<PipelineStatus> {
  const res = await api.get(`/documents/${docId}/status`)
  return res.data
}

// search

export interface SearchResult {
  document: Document
  relevance: number
}

export interface SearchResponse {
  query: string
  results: SearchResult[]
  total: number
  page: number
  page_size: number
}

export async function searchDocuments(query: string, page = 1): Promise<SearchResponse> {
  const res = await api.get('/search/', { params: { q: query, page } })
  return res.data
}

// stats

export interface Stats {
  total_documents: number
  completed: number
  failed: number
  in_progress: number
  avg_processing_time_ms: number | null
  documents_by_type: Record<string, number>
  documents_by_status: Record<string, number>
}

export async function getStats(): Promise<Stats> {
  const res = await api.get('/stats/')
  return res.data
}

// health

export async function healthCheck() {
  const res = await api.get('/health')
  return res.data
}

export default api
