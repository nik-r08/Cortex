import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getStats, type Stats } from '../api/client'

export default function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null)
  const [loading, setLoading] = useState(true)
  const [err, setErr] = useState(false)

  useEffect(() => {
    let cancelled = false
    loadStats()

    // poll every 10s if there are documents in progress
    const interval = setInterval(loadStats, 10000)
    return () => { cancelled = true; clearInterval(interval) }

    async function loadStats() {
      try {
        const data = await getStats()
        if (!cancelled) { setStats(data); setErr(false) }
      } catch {
        if (!cancelled) setErr(true)
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
  }, [])

  if (loading) return <Skeleton />
  if (err || !stats) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500 mb-2">Could not load stats</p>
        <button onClick={() => window.location.reload()} className="text-blue-600 text-sm hover:underline">
          Retry
        </button>
      </div>
    )
  }

  const cards = [
    { label: 'Total', value: stats.total_documents, color: 'text-gray-900' },
    { label: 'Completed', value: stats.completed, color: 'text-green-600' },
    { label: 'In Progress', value: stats.in_progress, color: 'text-blue-600' },
    { label: 'Failed', value: stats.failed, color: 'text-red-600' },
  ]

  const typeEntries = Object.entries(stats.documents_by_type)

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900">Overview</h2>
        <Link
          to="/upload"
          className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors"
        >
          Upload Document
        </Link>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {cards.map((c) => (
          <div key={c.label} className="bg-white border rounded-lg p-5">
            <p className="text-sm text-gray-500 mb-1">{c.label}</p>
            <p className={`text-3xl font-semibold ${c.color}`}>{c.value}</p>
          </div>
        ))}
      </div>

      {stats.avg_processing_time_ms !== null && (
        <div className="bg-white border rounded-lg p-5">
          <p className="text-sm text-gray-500 mb-1">Avg Processing Time</p>
          <p className="text-xl font-medium text-gray-900">
            {stats.avg_processing_time_ms < 1000
              ? `${Math.round(stats.avg_processing_time_ms)}ms`
              : `${(stats.avg_processing_time_ms / 1000).toFixed(1)}s`
            }
          </p>
        </div>
      )}

      {typeEntries.length > 0 && (
        <div className="bg-white border rounded-lg p-5">
          <h3 className="text-sm font-medium text-gray-700 mb-3">By Document Type</h3>
          <div className="space-y-2">
            {typeEntries.map(([type, count]) => (
              <div key={type} className="flex items-center justify-between text-sm">
                <span className="capitalize text-gray-600">{type}</span>
                <span className="font-medium text-gray-900">{count}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

function Skeleton() {
  return (
    <div className="space-y-8 animate-pulse">
      <div className="h-6 w-32 bg-gray-200 rounded" />
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {[1,2,3,4].map(i => (
          <div key={i} className="bg-white border rounded-lg p-5">
            <div className="h-4 w-16 bg-gray-200 rounded mb-2" />
            <div className="h-8 w-12 bg-gray-200 rounded" />
          </div>
        ))}
      </div>
    </div>
  )
}
