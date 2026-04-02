import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { getDocument } from '../api/client'
import StatusBadge from '../components/StatusBadge'

export default function DocumentDetail() {
  const { id } = useParams()
  const [doc, setDoc] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (id) {
      getDocument(id)
        .then(setDoc)
        .finally(() => setLoading(false))
    }
  }, [id])

  if (loading) return <p className="text-gray-500">Loading...</p>
  if (!doc) return <p className="text-red-500">Document not found</p>

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <h2 className="text-lg font-semibold">{doc.filename}</h2>
        <StatusBadge status={doc.status} />
      </div>

      <div className="grid grid-cols-2 gap-4 text-sm">
        <div>
          <span className="text-gray-500">Type:</span> {doc.document_type || 'Unknown'}
        </div>
        <div>
          <span className="text-gray-500">Size:</span> {(doc.file_size / 1024).toFixed(1)} KB
        </div>
        <div>
          <span className="text-gray-500">Uploaded:</span> {new Date(doc.created_at).toLocaleString()}
        </div>
      </div>

      {doc.extractions && doc.extractions.length > 0 && (
        <div>
          <h3 className="font-medium mb-2">Extracted Fields</h3>
          <div className="bg-gray-50 rounded p-4">
            <pre className="text-sm whitespace-pre-wrap">
              {JSON.stringify(doc.extractions[0].extracted_data, null, 2)}
            </pre>
          </div>
          <p className="text-xs text-gray-400 mt-1">
            Confidence: {(doc.extractions[0].confidence * 100).toFixed(0)}%
          </p>
        </div>
      )}
    </div>
  )
}
