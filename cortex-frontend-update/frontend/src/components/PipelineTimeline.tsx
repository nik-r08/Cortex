import type { ProcessingJob } from '../types'

interface Props {
  jobs: ProcessingJob[]
  totalMs: number | null
}

const stageLabels: Record<string, string> = {
  parsing: 'Parse',
  classifying: 'Classify',
  extracting: 'Extract',
  validating: 'Validate',
}

function statusIcon(status: string) {
  switch (status) {
    case 'completed':
      return (
        <svg className="h-4 w-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
        </svg>
      )
    case 'failed':
      return (
        <svg className="h-4 w-4 text-red-500" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
        </svg>
      )
    case 'running':
      return (
        <svg className="h-4 w-4 text-blue-500 animate-spin" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
      )
    default:
      return <div className="h-4 w-4 rounded-full border-2 border-gray-300" />
  }
}

export default function PipelineTimeline({ jobs, totalMs }: Props) {
  if (jobs.length === 0) {
    return <p className="text-gray-400 text-sm">No pipeline jobs</p>
  }

  return (
    <div>
      <div className="space-y-3">
        {jobs.map((job) => (
          <div key={job.id} className="flex items-center gap-3 text-sm">
            {statusIcon(job.status)}
            <span className="min-w-[80px] font-medium text-gray-700">
              {stageLabels[job.stage] || job.stage}
            </span>
            {job.duration_ms !== null && (
              <span className="text-gray-400 text-xs">
                {job.duration_ms < 1000
                  ? `${job.duration_ms}ms`
                  : `${(job.duration_ms / 1000).toFixed(1)}s`
                }
              </span>
            )}
            {job.error_message && (
              <span className="text-red-500 text-xs truncate max-w-[300px]" title={job.error_message}>
                {job.error_message}
              </span>
            )}
          </div>
        ))}
      </div>
      {totalMs !== null && (
        <p className="text-xs text-gray-400 mt-3 pt-2 border-t">
          Total: {totalMs < 1000 ? `${totalMs}ms` : `${(totalMs / 1000).toFixed(1)}s`}
        </p>
      )}
    </div>
  )
}
