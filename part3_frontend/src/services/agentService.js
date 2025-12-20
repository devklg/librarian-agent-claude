import axios from 'axios'

const API_URL = '/api'

const agentService = {
  async createSession() {
    const response = await axios.post(`${API_URL}/agent/chat/new`)
    return response.data.session_id
  },

  async sendMessage(sessionId, message, onChunk) {
    // Use Fetch API for SSE streaming (axios doesn't support it properly in browsers)
    const response = await fetch(`${API_URL}/agent/chat/${sessionId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message })
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()

    try {
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        
        const text = decoder.decode(value)
        const lines = text.split('\n')
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              // Handle different event types
              if (data.text) {
                onChunk(data.text)
              }
            } catch (e) {
              console.warn('Failed to parse SSE data:', line, e)
            }
          }
        }
      }
    } finally {
      reader.releaseLock()
    }
  },

  async getHistory(sessionId) {
    const response = await axios.get(`${API_URL}/agent/chat/${sessionId}/history`)
    return response.data
  }
}

export default agentService
