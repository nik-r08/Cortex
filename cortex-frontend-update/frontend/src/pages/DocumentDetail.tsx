import { useEffect, useState } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { getDocument, getExtractions, getPipelineStatus, deleteDocument } from '../api/client'
import type { ExtractionSummary, PipelineStatus } from '../api/client'
import type { Document } from '../types'
import StatusBadge from '../components/StatusBadge'
import ExtractionView from '../components/ExtractionView'
import PipelineTimeline from '../components/PipelineTimeline'

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

export default function DocumentDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [doc, setDoc] = useState<Document | null>(null)
  const [extractions, setExtractions] = useState<ExtractionSummary | null>(null)
  const [pipeline, setPipeline] = useState<PipelineStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [deleting, setDeleting] = useState(false)
  const [tab, setTab] = useState<'extractions' | 'pipeline' | 'raw'>('extractions')

  useEffect(() => {
    if (!id) return

    Promise.all([
      getDocument(id),
      getExtractions(id).catch(() => null),
      getPipelineStatus(id).catch(() => null),
    ]).then(([docData, extData, pipeData]) => {
      setDoc(docData)
      setExtractions(extData)
      setPipeline(pipeData)
    }).catch(() => {
      setDoc(null)
    }).finally(() => setLoading(false))
  }, [id])

  async function handleDelete() {
    if (!id || !confirm('Delete this document? This cannot be undone.')) return
    setDeleting(true)
    try {
      await deleteDocument(id)
      navigate('/documents')
    } catch {
      setDeleting(false)
    }
  }

  if (loading) {
    return (
      <div className="animate-pulse space-y-4">
        <div className="h-6 w-48 bg-gray-200 rounded" />
        <div className="h-4 w-32 bg-gray-200 rounded" />
        <div className="h-40 bg-gray-200 rounded-lg" />
      </div>
    )
  }

  if (!doc) {
    return (
      <div className="text-center py-16">
        <p className="text-gray-500 mb-2">Document not found</p>
        <Link to="/documents" className="text-blue-600 text-sm hover:underline">Back to documents</Link>
      </div>
    )
  }

  const tabs = [
    { key: 'extractions', label: 'Extractions' },
    { key: 'pipeline', label: 'Pipeline' },
    { key: 'raw', label: 'Raw Text' },
  ] as const

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2 text-sm text-gray-500">
        <Link to="/documents" className="hover:text-gray-700">Documents</Link>
        <span>/</span>
        <span className="text-gray-900">{doc.original_filename}</span>
      </div>

      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <h2 className="text-xl font-semibold text-gray-900">{doc.original_filename}</h2>
            <StatusBadge status={doc.status} />
          </div>
          <div className="flex gap-4 text-sm text-gray-500">
            {doc.document_type && <span className="capitalize">{doc.document_type}</span>}
            <span>{formatSize(doc.file_size)}</span>
            <span>{doc.content_type}</span>
            <span>{new Date(doc.created_at).toLocaleString()}</span>
          </div>
        </div>
        <button
          onClick={handleDelete}
          disabled={deleting}
          className="text-sm text-red-600 hover:text-red-700 disabled:opacity-50"
        >
          {deleting ? 'Deleting...' : 'Delete'}
        </button>
      </div>

      <div className="border-b">
        <div className="flex gap-6">
          {tabs.map(t => (
            <button
              key={t.key}
              onClick={() => setTab(t.key)}
              className={`pb-2 text-sm font-medium border-b-2 transition-colors ${
                tab === t.key
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>
      </div>

      <div className="bg-white border rounded-lg p-6">
        {tab === 'extractions' && extractions && (
          <ExtractionView
            extractions={extractions.extractions}
            avgConfidence={extractions.avg_confidence}
          />
        )}
        {tab === 'extractions' && !extractions && (
          <p className="text-gray-400 text-sm">No extraction data available</p>
        )}

        {tab === 'pipeline' && pipeline && (
          <PipelineTimeline jobs={pipeline.jobs} totalMs={pipeline.total_duration_ms} />
        )}
        {tab === 'pipeline' && !pipeline && (
          <p className="text-gray-400 text-sm">No pipeline data available</p>
        )}

        {tab === 'raw' && (
          <div className="max-h-96 overflow-y-auto">
            {doc.content_text ? (
              <pre className="text-sm text-gray-700 whitespace-pre-wrap font-mono leading-relaxed">
                {doc.content_text}
              </pre>
            ) : (
              <p className="text-gray-400 text-sm">No text content extracted</p>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
