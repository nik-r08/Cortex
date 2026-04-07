import type { Extraction } from '../types'

interface Props {
  extractions: Extraction[]
  avgConfidence: number
}

function confidenceColor(c: number): string {
  if (c >= 0.8) return 'text-green-600'
  if (c >= 0.5) return 'text-amber-600'
  return 'text-red-600'
}

export default function ExtractionView({ extractions, avgConfidence }: Props) {
  if (extractions.length === 0) {
    return <p className="text-gray-400 text-sm">No extractions yet</p>
  }

  return (
    <div>
      <div className="mb-3 flex items-center gap-2 text-sm">
        <span className="text-gray-500">Avg confidence:</span>
        <span className={`font-medium ${confidenceColor(avgConfidence)}`}>
          {(avgConfidence * 100).toFixed(0)}%
        </span>
      </div>
      <div className="bg-gray-50 rounded-lg border divide-y">
        {extractions.map((ext) => (
          <div key={ext.id} className="flex items-start gap-3 px-4 py-3 text-sm">
            <span className="text-gray-500 min-w-[140px] shrink-0 font-medium">
              {ext.field_name}
            </span>
            <span className="text-gray-900 flex-1 break-words">{ext.field_value}</span>
            <span className={`text-xs shrink-0 ${confidenceColor(ext.confidence)}`}>
              {(ext.confidence * 100).toFixed(0)}%
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
