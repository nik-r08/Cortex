import { useState, useEffect } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { searchDocuments, type SearchResult } from '../api/client'
import StatusBadge from '../components/StatusBadge'

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('en-US', {
    month: 'short', day: 'numeric', year: 'numeric',
  })
}

export default function Search() {
  const [searchParams, setSearchParams] = useSearchParams()
  const initialQuery = searchParams.get('q') || ''

  const [query, setQuery] = useState(initialQuery)
  const [results, setResults] = useState<SearchResult[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(!!initialQuery)

  useEffect(() => {
    if (initialQuery) doSearch(initialQuery)
  }, [])

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!query.trim()) return
    setSearchParams({ q: query })
    await doSearch(query)
  }

  async function doSearch(q: string) {
    setLoading(true)
    setSearched(true)
    try {
      const data = await searchDocuments(q)
      setResults(data.results)
      setTotal(data.total)
    } catch {
      setResults([])
      setTotal(0)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <h2 className="text-lg font-semibold text-gray-900">Search</h2>

      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search by content, filename, extracted fields..."
          className="flex-1 border rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        <button
          type="submit"
          disabled={loading || !query.trim()}
          className="bg-blue-600 text-white px-5 py-2.5 rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors"
        >
          {loading ? 'Searching...' : 'Search'}
        </button>
      </form>

      {loading && (
        <div className="space-y-3 animate-pulse">
          {[1,2,3].map(i => (
            <div key={i} className="bg-white border rounded-lg p-4">
              <div className="h-4 w-48 bg-gray-200 rounded mb-2" />
              <div className="h-3 w-full bg-gray-200 rounded" />
            </div>
          ))}
        </div>
      )}

      {!loading && searched && results.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500">No results for "{searchParams.get('q')}"</p>
          <p className="text-gray-400 text-sm mt-1">Try different keywords or check spelling</p>
        </div>
      )}

      {!loading && results.length > 0 && (
        <>
          <p className="text-sm text-gray-500">{total} result{total !== 1 ? 's' : ''}</p>
          <div className="space-y-3">
            {results.map((r) => (
              <div key={r.document.id} className="bg-white border rounded-lg p-4 hover:shadow-sm transition-shadow">
                <div className="flex items-center gap-2 mb-1">
                  <Link
                    to={`/documents/${r.document.id}`}
                    className="font-medium text-blue-600 hover:text-blue-800"
                  >
                    {r.document.original_filename}
                  </Link>
                  <StatusBadge status={r.document.status} />
                  {r.document.document_type && (
                    <span className="text-xs text-gray-400 capitalize">{r.document.document_type}</span>
                  )}
                </div>
                <div className="flex items-center gap-3 text-xs text-gray-400">
                  <span>{formatDate(r.document.created_at)}</span>
                  <span>Relevance: {(r.relevance * 100).toFixed(0)}%</span>
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  )
}
