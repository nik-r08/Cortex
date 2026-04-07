import { useNavigate } from 'react-router-dom'
import FileUpload from '../components/FileUpload'

export default function Upload() {
  const navigate = useNavigate()

  return (
    <div className="max-w-xl mx-auto space-y-4">
      <h2 className="text-lg font-semibold text-gray-900">Upload Document</h2>
      <p className="text-sm text-gray-500">
        Upload a PDF or text file. It will be processed through the pipeline
        automatically: parsing, classification, extraction, and validation.
      </p>
      <FileUpload onSuccess={() => navigate('/documents')} />
    </div>
  )
}
