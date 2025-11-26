import { useState, useRef, useEffect } from 'react'
import agentService from '../services/agentService'
import '../styles/AgentChat.css'

export default function AgentChat() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [sessionId, setSessionId] = useState(null)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    initSession()
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const initSession = async () => {
    const id = await agentService.createSession()
    setSessionId(id)
  }

  const handleSend = async (e) => {
    e.preventDefault()
    if (!input.trim() || !sessionId || loading) return

    const userMsg = input
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: userMsg }])
    setLoading(true)

    try {
      let fullResponse = ''
      await agentService.sendMessage(sessionId, userMsg, (chunk) => {
        fullResponse += chunk
        setMessages(prev => {
          const updated = [...prev]
          if (updated[updated.length - 1]?.role === 'assistant') {
            updated[updated.length - 1].content = fullResponse
          } else {
            updated.push({ role: 'assistant', content: chunk })
          }
          return updated
        })
      })
    } catch (error) {
      console.error('Error:', error)
      setMessages(prev => [...prev, { role: 'error', content: 'Error: ' + error.message }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="chat-container">
      <div className="aurora-background"></div>
      
      <div className="chat-header">
        <h1>Librarian Agent</h1>
        <p>Powered by Claude SDK</p>
      </div>

      <div className="messages">
        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.role}`}>
            {msg.content}
          </div>
        ))}
        {loading && <div className="typing-indicator">
          <span></span><span></span><span></span>
        </div>}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSend} className="input-form">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask me anything..."
          disabled={loading}
        />
        <button type="submit" disabled={loading}>Send</button>
      </form>
    </div>
  )
}
