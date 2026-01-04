import { useState, useRef } from 'react'

export default function FileUpload({ onUploadComplete }) {
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState(null)
  const fileInputRef = useRef(null)

  const handleUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    const formData = new FormData()
    formData.append('file', file)

    setUploading(true)
    setError(null)

    try {
      const response = await fetch('/api/documents/upload', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) throw new Error(`Upload failed: ${response.statusText}`)

      const result = await response.json()
      onUploadComplete?.(result)
    } catch (err) {
      setError(err.message)
    } finally {
      setUploading(false)
      if (fileInputRef.current) fileInputRef.current.value = ''
    }
  }

  return (
    <div className="file-upload">
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleUpload}
        accept=".pdf,.docx,.pptx,.xlsx,.txt,.md"
        hidden
      />
      <button
        onClick={() => fileInputRef.current?.click()}
        disabled={uploading}
        className="upload-btn"
        style={{
          padding: '8px 16px',
          background: uploading ? '#ccc' : '#4a90d9',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: uploading ? 'not-allowed' : 'pointer'
        }}
      >
        {uploading ? 'Uploading...' : '📎 Upload'}
      </button>
      {error && <span style={{ color: 'red', marginLeft: '10px' }}>{error}</span>}
    </div>
  )
}
