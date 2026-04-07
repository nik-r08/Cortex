import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { getDocuments, type DocumentListResponse } from '../api/client'
import StatusBadge from '../components/StatusBadge'
import type { Document } from '../types'

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('en-US', {
    month: 'short', day: 'numeric', year: 'numeric',
  })
}

export default function DocumentList() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [data, setData] = useState<DocumentListResponse | null>(null)
  const [loading, setLoading] = useState(true)

  const page = parseInt(searchParams.get('page') || '1')
  const typeFilter = searchParams.get('type') || ''
  const statusFilter = searchParams.get('status') || ''

  useEffect(() => {
    setLoading(true)
    const params: Record<string, string | number> = { page }
    if (typeFilter) params.document_type = typeFilter
    if (statusFilter) params.status = statusFilter

    getDocuments(params as any)
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false))
  }, [page, typeFilter, statusFilter])

  function setFilter(key: string, val: string) {
    const next = new URLSearchParams(searchParams)
    if (val) next.set(key, val)
    else next.delete(key)
    next.set('page', '1')
    setSearchParams(next)
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900">Documents</h2>
        <Link
          to="/upload"
          className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors"
        >
          Upload
        </Link>
      </div>

      <div className="flex gap-3">
        <select
          value={typeFilter}
          onChange={(e) => setFilter('type', e.target.value)}
          className="border rounded-lg px-3 py-1.5 text-sm bg-white"
        >
          <option value="">All types</option>
          <option value="invoice">Invoice</option>
          <option value="resume">Resume</option>
          <option value="contract">Contract</option>
          <option value="report">Report</option>
          <option value="other">Other</option>
        </select>
        <select
          value={statusFilter}
          onChange={(e) => setFilter('status', e.target.value)}
          className="border rounded-lg px-3 py-1.5 text-sm bg-white"
        >
          <option value="">All statuses</option>
          <option value="uploaded">Uploaded</option>
          <option value="completed">Completed</option>
          <option value="failed">Failed</option>
        </select>
      </div>

      {loading ? (
        <TableSkeleton />
      ) : !data || data.documents.length === 0 ? (
        <EmptyState />
      ) : (
        <>
          <div className="bg-white border rounded-lg overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-500 border-b bg-gray-50">
                  <th className="px-4 py-3 font-medium">File</th>
                  <th className="px-4 py-3 font-medium">Type</th>
                  <th className="px-4 py-3 font-medium">Status</th>
                  <th className="px-4 py-3 font-medium">Size</th>
                  <th className="px-4 py-3 font-medium">Uploaded</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {data.documents.map((doc: Document) => (
                  <tr key={doc.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-4 py-3">
                      <Link to={`/documents/${doc.id}`} className="text-blue-600 hover:text-blue-800 font-medium">
                        {doc.original_filename}
                      </Link>
                    </td>
                    <td className="px-4 py-3 capitalize text-gray-600">{doc.document_type || '\u2014'}</td>
                    <td className="px-4 py-3"><StatusBadge status={doc.status} /></td>
                    <td className="px-4 py-3 text-gray-500">{formatSize(doc.file_size)}</td>
                    <td className="px-4 py-3 text-gray-500">{formatDate(doc.created_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {(data.has_next || page > 1) && (
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-500">
                Page {data.page} of {Math.ceil(data.total / data.page_size)}
                {' '}({data.total} total)
              </span>
              <div className="flex gap-2">
                <button
                  disabled={page <= 1}
                  onClick={() => setFilter('page', String(page - 1))}
                  className="px-3 py-1 border rounded hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed"
                >
                  Prev
                </button>
                <button
                  disabled={!data.has_next}
                  onClick={() => { const n = new URLSearchParams(searchParams); n.set('page', String(page + 1)); setSearchParams(n) }}
                  className="px-3 py-1 border rounded hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed"
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}

function EmptyState() {
  return (
    <div className="text-center py-16">
      <svg className="mx-auto h-12 w-12 text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
          d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m6.75 12H9.75m0 0l2.25 2.25M9.75 14.25l2.25-2.25M3.375 20.25h17.25c.621 0 1.125-.504 1.125-1.125V5.625c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125v13.5c0 .621.504 1.125 1.125 1.125z" />
      </svg>
      <p className="text-gray-500 mb-1">No documents yet</p>
      <Link to="/upload" className="text-blue-600 text-sm hover:underline">Upload your first document</Link>
    </div>
  )
}

function TableSkeleton() {
  return (
    <div className="bg-white border rounded-lg overflow-hidden animate-pulse">
      <div className="border-b bg-gray-50 h-10" />
      {[1,2,3,4,5].map(i => (
        <div key={i} className="flex items-center gap-4 px-4 py-3 border-b last:border-0">
          <div className="h-4 w-40 bg-gray-200 rounded" />
          <div className="h-4 w-16 bg-gray-200 rounded" />
          <div className="h-4 w-20 bg-gray-200 rounded" />
          <div className="h-4 w-14 bg-gray-200 rounded" />
          <div className="h-4 w-24 bg-gray-200 rounded" />
        </div>
      ))}
    </div>
  )
}
