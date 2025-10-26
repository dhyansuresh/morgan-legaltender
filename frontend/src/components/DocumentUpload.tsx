import { useState, useRef } from 'react'
import { Upload, FileText, Image, File, AlertCircle, CheckCircle, Loader2, X } from 'lucide-react'
import { TaskRouteResponse } from '../services/api'

interface DocumentUploadProps {
  onResult: (result: TaskRouteResponse) => void
  onLoadingChange: (loading: boolean) => void
}

export default function DocumentUpload({ onResult, onLoadingChange }: DocumentUploadProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [error, setError] = useState('')
  const [caseId, setCaseId] = useState('')
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    // Validate file size (50MB max)
    if (file.size > 50 * 1024 * 1024) {
      setError('File size exceeds 50MB limit')
      return
    }

    setSelectedFile(file)
    setError('')

    // Create preview for images
    if (file.type.startsWith('image/')) {
      const reader = new FileReader()
      reader.onloadend = () => {
        setPreview(reader.result as string)
      }
      reader.readAsDataURL(file)
    } else {
      setPreview(null)
    }
  }

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select a file')
      return
    }

    setError('')
    onLoadingChange(true)

    try {
      const formData = new FormData()
      formData.append('file', selectedFile)
      if (caseId) {
        formData.append('case_id', caseId)
      }
      formData.append('auto_process', 'true')

      const response = await fetch('http://localhost:8000/api/documents/upload', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Upload failed')
      }

      const data = await response.json()

      // Transform the response to match TaskRouteResponse format
      if (data.orchestrator_result) {
        onResult({
          status: 'success',
          message: data.message,
          data: data.orchestrator_result
        })
      }

      // Clear form
      setSelectedFile(null)
      setPreview(null)
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }

    } catch (err: any) {
      setError(err.message || 'Failed to upload document. Please try again.')
    } finally {
      onLoadingChange(false)
    }
  }

  const getFileIcon = (type: string) => {
    if (type.startsWith('image/')) return <Image size={24} />
    if (type === 'application/pdf') return <FileText size={24} />
    return <File size={24} />
  }

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
  }

  return (
    <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl shadow-2xl border border-slate-700 p-8">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-white mb-2">Upload Document</h2>
        <p className="text-slate-400">
          Upload PDFs, images, or documents for automatic text extraction and AI analysis
        </p>
      </div>

      <div className="space-y-6">
        {/* File Upload Area */}
        <div>
          <label
            htmlFor="file-upload"
            className="block w-full cursor-pointer"
          >
            <div className={`border-2 border-dashed rounded-lg p-8 text-center transition-all ${
              selectedFile
                ? 'border-blue-500 bg-blue-500/10'
                : 'border-slate-600 hover:border-slate-500 bg-slate-900/50'
            }`}>
              {selectedFile ? (
                <div className="space-y-4">
                  {preview && (
                    <div className="max-w-md mx-auto">
                      <img
                        src={preview}
                        alt="Preview"
                        className="rounded-lg max-h-48 mx-auto"
                      />
                    </div>
                  )}
                  <div className="flex items-center justify-center space-x-3">
                    <div className="text-blue-400">
                      {getFileIcon(selectedFile.type)}
                    </div>
                    <div className="text-left">
                      <p className="text-white font-medium">{selectedFile.name}</p>
                      <p className="text-slate-400 text-sm">{formatFileSize(selectedFile.size)}</p>
                    </div>
                    <button
                      type="button"
                      onClick={(e) => {
                        e.preventDefault()
                        setSelectedFile(null)
                        setPreview(null)
                        if (fileInputRef.current) {
                          fileInputRef.current.value = ''
                        }
                      }}
                      className="text-slate-400 hover:text-red-400 transition-colors"
                    >
                      <X size={20} />
                    </button>
                  </div>
                </div>
              ) : (
                <div className="space-y-3">
                  <Upload className="mx-auto text-slate-400" size={48} />
                  <div>
                    <p className="text-white font-medium">Click to upload or drag and drop</p>
                    <p className="text-slate-400 text-sm mt-1">
                      PDF, JPG, PNG, Word, Excel (Max 50MB)
                    </p>
                  </div>
                </div>
              )}
            </div>
          </label>
          <input
            ref={fileInputRef}
            id="file-upload"
            type="file"
            onChange={handleFileSelect}
            accept=".pdf,.jpg,.jpeg,.png,.gif,.bmp,.tiff,.doc,.docx,.xls,.xlsx,.txt"
            className="hidden"
          />
        </div>

        {/* Case ID Input */}
        <div>
          <label htmlFor="case-id" className="block text-sm font-medium text-slate-300 mb-2">
            Case ID (Optional)
          </label>
          <input
            id="case-id"
            type="text"
            value={caseId}
            onChange={(e) => setCaseId(e.target.value)}
            placeholder="e.g., CASE-2024-001"
            className="w-full px-4 py-3 bg-slate-900/50 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Supported Formats Info */}
        <div className="bg-blue-900/20 border border-blue-800 rounded-lg p-4">
          <div className="flex items-start space-x-2">
            <CheckCircle className="text-blue-400 flex-shrink-0 mt-0.5" size={18} />
            <div className="text-sm text-blue-300">
              <p className="font-medium mb-1">Automatic Processing:</p>
              <ul className="list-disc list-inside space-y-1 text-blue-200/80">
                <li>Text extraction from PDFs (including scanned documents with OCR)</li>
                <li>OCR for images (JPG, PNG, etc.)</li>
                <li>AI task detection and routing</li>
                <li>Specialist assignment based on content</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="flex items-start space-x-2 p-4 bg-red-900/20 border border-red-800 rounded-lg">
            <AlertCircle className="text-red-500 flex-shrink-0 mt-0.5" size={18} />
            <p className="text-red-400 text-sm">{error}</p>
          </div>
        )}

        {/* Upload Button */}
        <button
          onClick={handleUpload}
          disabled={!selectedFile}
          className="w-full flex items-center justify-center space-x-2 px-6 py-4 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-700 disabled:cursor-not-allowed text-white font-semibold rounded-lg transition-colors shadow-lg"
        >
          <Upload size={20} />
          <span>Upload and Process</span>
        </button>
      </div>
    </div>
  )
}
