import { useState, useCallback, useRef } from 'react'
import { uploadDocument } from '../api/client'

interface Props {
  onSuccess: () => void
}

export default function FileUpload({ onSuccess }: Props) {
  const [dragging, setDragging] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const fileRef = useRef<HTMLInputElement>(null)

  const handleDrop = useCallback(async (e: React.DragEvent) => {
    e.preventDefault()
    setDragging(false)
    const file = e.dataTransfer.files[0]
    if (file) await doUpload(file)
  }, [])

  async function handleFileSelect(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (file) await doUpload(file)
  }

  async function doUpload(file: File) {
    setError(null)
    setUploading(true)
    try {
      await uploadDocument(file)
      onSuccess()
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Upload failed'
      setError(typeof msg === 'string' ? msg : JSON.stringify(msg))
    } finally {
      setUploading(false)
      if (fileRef.current) fileRef.current.value = ''
    }
  }

  return (
    <div
      className={`border-2 border-dashed rounded-lg p-10 text-center transition-colors ${
        dragging ? 'border-blue-400 bg-blue-50' : 'border-gray-300 hover:border-gray-400'
      }`}
      onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
      onDragLeave={() => setDragging(false)}
      onDrop={handleDrop}
    >
      {uploading ? (
        <div className="flex items-center justify-center gap-2 text-gray-500">
          <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
          Uploading...
        </div>
      ) : (
        <>
          <svg className="mx-auto h-10 w-10 text-gray-400 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
              d="M12 16V4m0 0L8 8m4-4l4 4M4 14v4a2 2 0 002 2h12a2 2 0 002-2v-4" />
          </svg>
          <p className="text-gray-600 mb-1">Drop a file here or click to browse</p>
          <input
            ref={fileRef}
            type="file"
            onChange={handleFileSelect}
            accept=".pdf,.txt,.png,.jpg,.jpeg"
            className="hidden"
            id="file-upload"
          />
          <label htmlFor="file-upload" className="cursor-pointer text-blue-600 hover:text-blue-700 text-sm">
            Choose file
          </label>
          <p className="text-xs text-gray-400 mt-2">PDF, TXT, PNG, JPEG up to 10MB</p>
        </>
      )}
      {error && <p className="text-red-500 mt-3 text-sm">{error}</p>}
    </div>
  )
}
