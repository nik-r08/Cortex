interface Props {
  data: Record<string, any>
  confidence: number
}

export default function ExtractionView({ data, confidence }: Props) {
  const entries = Object.entries(data)

  return (
    <div className="space-y-2">
      {entries.map(([key, value]) => (
        <div key={key} className="flex gap-2 text-sm">
          <span className="text-gray-500 min-w-[120px]">{key}:</span>
          <span>{typeof value === 'object' ? JSON.stringify(value) : String(value)}</span>
        </div>
      ))}
      <div className="mt-3 pt-2 border-t text-xs text-gray-400">
        Confidence: {(confidence * 100).toFixed(0)}%
      </div>
    </div>
  )
}
