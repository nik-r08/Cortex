import { useState } from 'react'
import { searchDocuments } from '../api/client'
import StatusBadge from '../components/StatusBadge'

export default function Search() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)

  async function handleSearch(e: React.FormEvent) {
    e.preventDefault()
    if (!query.trim()) return
    setLoading(true)
    setSearched(true)
    try {
      const data = await searchDocuments(query)
      setResults(data.results || [])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <form onSubmit={handleSearch} className="flex gap-2 mb-6">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search documents..."
          className="flex-1 border rounded px-3 py-2"
        />
        <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
          Search
        </button>
      </form>

      {loading && <p className="text-gray-500">Searching...</p>}

      {!loading && searched && results.length === 0 && (
        <p className="text-gray-400 text-center py-8">No results found</p>
      )}

      <div className="space-y-3">
        {results.map((r: any) => (
          <div key={r.id} className="border rounded p-4 hover:bg-gray-50">
            <div className="flex items-center gap-2 mb-1">
              <a href={`/documents/${r.id}`} className="font-medium text-blue-600 hover:underline">
                {r.filename}
              </a>
              <StatusBadge status={r.status} />
            </div>
            {r.snippet && (
              <p className="text-sm text-gray-600" dangerouslySetInnerHTML={{ __html: r.snippet }} />
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
