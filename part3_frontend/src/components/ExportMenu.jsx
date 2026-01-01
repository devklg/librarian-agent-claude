import { useState } from 'react'

export default function ExportMenu({ sessionId }) {
  const [exporting, setExporting] = useState(false)

  const handleExport = async (format) => {
    setExporting(true)
    try {
      const response = await fetch(`/api/agent/chat/${sessionId}/export/${format}`)

      if (format === 'json') {
        const data = await response.json()
        downloadFile(JSON.stringify(data, null, 2), `conversation-${sessionId}.json`, 'application/json')
      } else if (format === 'markdown') {
        const text = await response.text()
        downloadFile(text, `conversation-${sessionId}.md`, 'text/markdown')
      } else if (format === 'html') {
        const text = await response.text()
        downloadFile(text, `conversation-${sessionId}.html`, 'text/html')
      }
    } catch (error) {
      console.error('Export failed:', error)
    } finally {
      setExporting(false)
    }
  }

  const downloadFile = (content, filename, type) => {
    const blob = new Blob([content], { type })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="export-menu" style={{ display: 'flex', gap: '8px' }}>
      <button
        onClick={() => handleExport('json')}
        disabled={exporting}
        style={{ padding: '6px 12px', cursor: 'pointer' }}
      >
        📄 JSON
      </button>
      <button
        onClick={() => handleExport('markdown')}
        disabled={exporting}
        style={{ padding: '6px 12px', cursor: 'pointer' }}
      >
        📝 Markdown
      </button>
      <button
        onClick={() => handleExport('html')}
        disabled={exporting}
        style={{ padding: '6px 12px', cursor: 'pointer' }}
      >
        🌐 HTML
      </button>
    </div>
  )
}
