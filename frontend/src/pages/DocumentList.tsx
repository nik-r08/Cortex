import { useEffect, useState } from 'react'
import { getDocuments } from '../api/client'
import StatusBadge from '../components/StatusBadge'

interface Doc {
  id: string
  filename: string
  document_type: string | null
  status: string
  created_at: string
}

export default function DocumentList() {
  const [docs, setDocs] = useState<Doc[]>([])
  const [loading, setLoading] = useState(true)
  const [typeFilter, setTypeFilter] = useState('')

  useEffect(() => {
    loadDocs()
  }, [typeFilter])

  async function loadDocs() {
    setLoading(true)
    try {
      const params: Record<string, string> = {}
      if (typeFilter) params.document_type = typeFilter
      const data = await getDocuments(params)
      setDocs(data.documents || [])
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <p className="text-gray-500">Loading...</p>

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-semibold">Documents</h2>
        <select
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
          className="border rounded px-2 py-1 text-sm"
        >
          <option value="">All types</option>
          <option value="invoice">Invoice</option>
          <option value="resume">Resume</option>
          <option value="contract">Contract</option>
          <option value="report">Report</option>
        </select>
      </div>
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left border-b">
            <th className="py-2">Filename</th>
            <th>Type</th>
            <th>Status</th>
            <th>Uploaded</th>
          </tr>
        </thead>
        <tbody>
          {docs.map((doc) => (
            <tr key={doc.id} className="border-b hover:bg-gray-50">
              <td className="py-2">
                <a href={`/documents/${doc.id}`} className="text-blue-600 hover:underline">
                  {doc.filename}
                </a>
              </td>
              <td>{doc.document_type || '—'}</td>
              <td><StatusBadge status={doc.status} /></td>
              <td className="text-gray-500">{new Date(doc.created_at).toLocaleDateString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {docs.length === 0 && <p className="text-gray-400 text-center py-8">No documents yet</p>}
    </div>
  )
}
// filter component for document type selector
