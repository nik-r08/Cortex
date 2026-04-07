import { useEffect, useState } from 'react'
import { getStats } from '../api/client'

export default function Dashboard() {
  const [stats, setStats] = useState<any>(null)

  useEffect(() => {
    getStats().then(setStats).catch(() => {})
  }, [])

  return (
    <div>
      <h2 className="text-lg font-semibold mb-4">Overview</h2>
      {stats ? (
        <div className="grid grid-cols-4 gap-4">
          <StatCard label="Total Documents" value={stats.total_documents} />
          <StatCard label="Processed" value={stats.processed} />
          <StatCard label="Processing" value={stats.processing} />
          <StatCard label="Failed" value={stats.failed} />
        </div>
      ) : (
        <p className="text-gray-500">Loading stats...</p>
      )}
    </div>
  )
}

function StatCard({ label, value }: { label: string; value: number }) {
  return (
    <div className="bg-white rounded-lg border p-4">
      <p className="text-sm text-gray-500">{label}</p>
      <p className="text-2xl font-semibold mt-1">{value}</p>
    </div>
  )
}
