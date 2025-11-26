import axios from 'axios'

const API_URL = '/api'

const agentService = {
  async createSession() {
    const response = await axios.post(`${API_URL}/agent/chat/new`)
    return response.data.session_id
  },

  async sendMessage(sessionId, message, onChunk) {
    const response = await axios.post(
      `${API_URL}/agent/chat/${sessionId}`,
      { message },
      { responseType: 'stream' }
    )

    const reader = response.data.getReader()
    const decoder = new TextDecoder()

    try {
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        
        const text = decoder.decode(value)
        const lines = text.split('\n')
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = JSON.parse(line.slice(6))
            if (data.content) onChunk(data.content)
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
