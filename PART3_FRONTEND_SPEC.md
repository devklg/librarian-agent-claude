# Part 3: Frontend Chat Interface Specification

**React chat UI with Aurora background and real-time streaming**

---

## 🎯 Your Mission

Build a beautiful React chat interface with:
- Aurora animated background (already designed!)
- Real-time message streaming
- Tool execution visualization
- Cost tracking
- Session management

---

## 📋 Requirements

### Technology Stack
- **Framework**: React 18+ with Vite
- **Routing**: React Router
- **HTTP**: Fetch API / Axios
- **Streaming**: EventSource (SSE)
- **Styling**: CSS with Aurora background

---

## 📁 File Structure

```
part3_frontend/
├── src/
│   ├── pages/
│   │   ├── AgentChat.jsx           # Main chat interface
│   │   ├── AgentChat.css           # Chat styling
│   │   ├── Dashboard.jsx           # Existing dashboard
│   │   ├── Catalog.jsx             # Existing catalog
│   │   └── Ingest.jsx              # Existing ingest
│   ├── components/
│   │   ├── MessageStream.jsx       # Streaming messages
│   │   ├── MessageBubble.jsx       # Individual message
│   │   ├── ToolExecutionDisplay.jsx # Tool visualization
│   │   ├── CostTracker.jsx         # Cost display
│   │   └── TypingIndicator.jsx     # Loading animation
│   ├── services/
│   │   └── agentService.js         # API communication
│   ├── App.jsx                     # Router with nav
│   ├── App.css                     # Aurora background
│   └── main.jsx                    # Entry point
├── index.html
├── vite.config.js
├── package.json
└── README.md
```

---

## 🎨 Design Requirements

### Aurora Background (Already Provided!)

Use the existing aurora background from App.css:

```css
@keyframes aurora {
  0% { transform: scale(1) rotate(0deg); opacity: 0.5; }
  50% { transform: scale(1.2) rotate(180deg); opacity: 0.8; }
  100% { transform: scale(1) rotate(360deg); opacity: 0.5; }
}

.app::before {
  content: '';
  position: fixed;
  inset: 0;
  z-index: 0;
  background: linear-gradient(45deg, #1a1a1a 0%, #003366 100%),
    repeating-linear-gradient(...);
  animation: aurora 8s linear infinite;
}
```

### Color Scheme

- **Primary**: Cyan `#00ffff`
- **Secondary**: Green `#00ff00`
- **Background**: Dark with glass morphism
- **Text**: White `#ffffff`
- **Accents**: Cyan/Green gradients

---

## 💬 Chat Interface Layout

```
┌────────────────────────────────────────────────┐
│  📚 Librarian Agent  │  Session: abc-123    💰 │ ← Header
├────────────────────────────────────────────────┤
│                                                │
│  ┌──────────────────────────────────┐         │
│  │  User: How do I create PowerPoint? │      │ ← User message (right)
│  └──────────────────────────────────┘         │
│                                                │
│  ┌──────────────────────────────────────────┐ │
│  │ 🤖 Librarian: Let me help you...        │ │ ← Agent message (left)
│  │                                          │ │
│  │ [Tool: query_skill(pptx)] ✓             │ │ ← Tool execution
│  │                                          │ │
│  │ Here's how to create a professional...  │ │
│  └──────────────────────────────────────────┘ │
│                                                │
│  ⏳ Librarian is typing...                    │ ← Typing indicator
│                                                │
├────────────────────────────────────────────────┤
│  💬 Type your message...            [Send] 🚀  │ ← Input area
└────────────────────────────────────────────────┘
```

---

## 🔧 Components to Build

### 1. AgentChat.jsx (Main Page)

```jsx
import React, { useState, useEffect, useRef } from 'react';
import MessageStream from '../components/MessageStream';
import CostTracker from '../components/CostTracker';
import { createSession, sendMessage } from '../services/agentService';
import './AgentChat.css';

function AgentChat() {
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [totalCost, setTotalCost] = useState(0);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    // Create session on mount
    initSession();
  }, []);

  const initSession = async () => {
    const session = await createSession();
    setSessionId(session.session_id);
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || !sessionId) return;

    // Add user message
    const userMsg = {
      type: 'user',
      content: inputMessage,
      timestamp: Date.now()
    };
    setMessages(prev => [...prev, userMsg]);
    setInputMessage('');
    setIsStreaming(true);

    // Start streaming agent response
    const agentMsg = {
      type: 'agent',
      content: '',
      toolCalls: [],
      timestamp: Date.now()
    };
    setMessages(prev => [...prev, agentMsg]);

    // Stream response
    await sendMessage(sessionId, inputMessage, {
      onContent: (text) => {
        setMessages(prev => {
          const updated = [...prev];
          updated[updated.length - 1].content += text;
          return updated;
        });
      },
      onToolCall: (tool) => {
        setMessages(prev => {
          const updated = [...prev];
          updated[updated.length - 1].toolCalls.push(tool);
          return updated;
        });
      },
      onEnd: (data) => {
        setTotalCost(prev => prev + data.cost.total);
        setIsStreaming(false);
      }
    });

    // Scroll to bottom
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="agent-chat">
      {/* Header */}
      <div className="chat-header">
        <h1>📚 Librarian Agent</h1>
        <div className="session-info">
          <span>Session: {sessionId?.slice(0, 8)}...</span>
          <CostTracker cost={totalCost} />
        </div>
      </div>

      {/* Messages */}
      <div className="messages-container">
        <MessageStream messages={messages} />
        {isStreaming && <TypingIndicator />}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="chat-input">
        <textarea
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              handleSendMessage();
            }
          }}
          placeholder="Ask me anything..."
          disabled={isStreaming}
        />
        <button 
          onClick={handleSendMessage}
          disabled={isStreaming || !inputMessage.trim()}
        >
          🚀 Send
        </button>
      </div>
    </div>
  );
}

export default AgentChat;
```

### 2. MessageBubble.jsx

```jsx
import React from 'react';
import ToolExecutionDisplay from './ToolExecutionDisplay';

function MessageBubble({ message }) {
  const isUser = message.type === 'user';

  return (
    <div className={`message-bubble ${isUser ? 'user' : 'agent'}`}>
      {/* Avatar */}
      <div className="avatar">
        {isUser ? '👤' : '🤖'}
      </div>

      {/* Content */}
      <div className="message-content">
        <div className="message-text">{message.content}</div>

        {/* Tool calls */}
        {message.toolCalls?.length > 0 && (
          <div className="tool-calls">
            {message.toolCalls.map((tool, idx) => (
              <ToolExecutionDisplay key={idx} tool={tool} />
            ))}
          </div>
        )}

        {/* Timestamp */}
        <div className="message-time">
          {new Date(message.timestamp).toLocaleTimeString()}
        </div>
      </div>
    </div>
  );
}

export default MessageBubble;
```

### 3. MessageStream.jsx

```jsx
import React from 'react';
import MessageBubble from './MessageBubble';

function MessageStream({ messages }) {
  return (
    <div className="message-stream">
      {messages.length === 0 && (
        <div className="welcome-message">
          <h2>👋 Hello! I'm the Librarian Agent</h2>
          <p>Ask me anything about:</p>
          <ul>
            <li>📄 Creating documents (Word, PowerPoint, Excel, PDF)</li>
            <li>💻 Framework documentation (Telnyx, Claude, React, etc.)</li>
            <li>🎨 Design and branding</li>
            <li>📚 Stored knowledge in the Universal Memory Bridge</li>
          </ul>
        </div>
      )}

      {messages.map((msg, idx) => (
        <MessageBubble key={idx} message={msg} />
      ))}
    </div>
  );
}

export default MessageStream;
```

### 4. ToolExecutionDisplay.jsx

```jsx
import React, { useState } from 'react';

function ToolExecutionDisplay({ tool }) {
  const [expanded, setExpanded] = useState(false);

  const getToolIcon = (name) => {
    const icons = {
      'search_documentation': '🔍',
      'load_documentation': '📥',
      'query_skill': '📚',
      'update_knowledge_graph': '🕸️',
      'get_catalog': '📋'
    };
    return icons[name] || '🛠️';
  };

  return (
    <div className="tool-execution">
      <div 
        className="tool-header"
        onClick={() => setExpanded(!expanded)}
      >
        <span className="tool-icon">{getToolIcon(tool.name)}</span>
        <span className="tool-name">{tool.name}</span>
        <span className="tool-status">✓</span>
        <button className="expand-btn">
          {expanded ? '▼' : '▶'}
        </button>
      </div>

      {expanded && (
        <div className="tool-details">
          <pre>{JSON.stringify(tool.input, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}

export default ToolExecutionDisplay;
```

### 5. CostTracker.jsx

```jsx
import React, { useState } from 'react';

function CostTracker({ cost }) {
  const [showDetails, setShowDetails] = useState(false);

  return (
    <div className="cost-tracker">
      <div 
        className="cost-display"
        onClick={() => setShowDetails(!showDetails)}
      >
        💰 ${cost.toFixed(4)}
      </div>

      {showDetails && (
        <div className="cost-details">
          <div className="cost-item">
            <span>Total Spent:</span>
            <span>${cost.toFixed(4)}</span>
          </div>
          <div className="cost-savings">
            <span>💡 Tip:</span>
            <span>Cache saves ~90%!</span>
          </div>
        </div>
      )}
    </div>
  );
}

export default CostTracker;
```

### 6. TypingIndicator.jsx

```jsx
import React from 'react';

function TypingIndicator() {
  return (
    <div className="typing-indicator">
      <div className="avatar">🤖</div>
      <div className="typing-dots">
        <span></span>
        <span></span>
        <span></span>
      </div>
    </div>
  );
}

export default TypingIndicator;
```

---

## 🌐 API Service

```javascript
// src/services/agentService.js

const API_BASE = 'http://localhost:9600';

export async function createSession() {
  const response = await fetch(`${API_BASE}/api/agent/chat/new`, {
    method: 'POST'
  });
  return response.json();
}

export async function sendMessage(sessionId, message, callbacks) {
  const response = await fetch(`${API_BASE}/api/agent/chat/${sessionId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      message,
      requester_id: 'user',
      requester_type: 'human'
    })
  });

  // Handle SSE stream
  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value);
    const lines = chunk.split('\n\n');

    for (const line of lines) {
      if (!line.trim()) continue;

      const [eventLine, dataLine] = line.split('\n');
      if (!dataLine) continue;

      const event = eventLine.replace('event: ', '');
      const data = JSON.parse(dataLine.replace('data: ', ''));

      if (event === 'content') {
        callbacks.onContent(data.text);
      } else if (event === 'tool_call') {
        callbacks.onToolCall(data);
      } else if (event === 'message_end') {
        callbacks.onEnd(data);
      }
    }
  }
}

export async function getHistory(sessionId) {
  const response = await fetch(`${API_BASE}/api/agent/chat/${sessionId}/history`);
  return response.json();
}

export async function getStats(sessionId) {
  const response = await fetch(`${API_BASE}/api/agent/chat/${sessionId}/stats`);
  return response.json();
}
```

---

## 🎨 CSS Styling

```css
/* AgentChat.css */

.agent-chat {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 80px);
  max-width: 1200px;
  margin: 0 auto;
}

/* Header */
.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px 12px 0 0;
}

.session-info {
  display: flex;
  gap: 1rem;
  align-items: center;
  color: #94a3b8;
  font-size: 0.875rem;
}

/* Messages */
.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
  background: rgba(0, 0, 0, 0.2);
}

.message-bubble {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.message-bubble.user {
  flex-direction: row-reverse;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(0, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  flex-shrink: 0;
}

.message-content {
  max-width: 70%;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 1rem;
}

.message-bubble.user .message-content {
  background: rgba(0, 255, 255, 0.1);
  border-color: rgba(0, 255, 255, 0.3);
}

.message-text {
  color: #ffffff;
  line-height: 1.6;
  margin-bottom: 0.5rem;
}

.message-time {
  font-size: 0.75rem;
  color: #64748b;
  text-align: right;
}

/* Tool Execution */
.tool-execution {
  margin-top: 0.75rem;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(0, 255, 255, 0.2);
  border-radius: 8px;
  padding: 0.75rem;
}

.tool-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.tool-icon {
  font-size: 1.25rem;
}

.tool-name {
  flex: 1;
  color: #00ffff;
  font-weight: 600;
  font-size: 0.875rem;
}

.tool-status {
  color: #10b981;
}

.tool-details {
  margin-top: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.tool-details pre {
  color: #94a3b8;
  font-size: 0.75rem;
  overflow-x: auto;
}

/* Typing Indicator */
.typing-indicator {
  display: flex;
  gap: 1rem;
  align-items: center;
  margin-bottom: 1.5rem;
}

.typing-dots {
  display: flex;
  gap: 0.5rem;
}

.typing-dots span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #00ffff;
  animation: bounce 1.4s infinite ease-in-out;
}

.typing-dots span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-dots span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

/* Input Area */
.chat-input {
  display: flex;
  gap: 1rem;
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0 0 12px 12px;
}

.chat-input textarea {
  flex: 1;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: #ffffff;
  font-family: inherit;
  font-size: 1rem;
  resize: none;
  min-height: 60px;
}

.chat-input textarea:focus {
  outline: none;
  border-color: rgba(0, 255, 255, 0.5);
  box-shadow: 0 0 12px rgba(0, 255, 255, 0.2);
}

.chat-input button {
  padding: 1rem 2rem;
  background: linear-gradient(135deg, rgba(0, 255, 255, 0.2), rgba(0, 255, 0, 0.2));
  border: 1px solid rgba(0, 255, 255, 0.4);
  border-radius: 8px;
  color: #ffffff;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s;
}

.chat-input button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 255, 255, 0.3);
}

.chat-input button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Welcome Message */
.welcome-message {
  text-align: center;
  padding: 3rem;
  color: #ffffff;
}

.welcome-message h2 {
  margin-bottom: 1rem;
  font-size: 2rem;
}

.welcome-message ul {
  list-style: none;
  padding: 0;
}

.welcome-message li {
  margin: 0.5rem 0;
  font-size: 1.125rem;
}

/* Cost Tracker */
.cost-tracker {
  position: relative;
}

.cost-display {
  padding: 0.5rem 1rem;
  background: rgba(16, 185, 129, 0.2);
  border: 1px solid rgba(16, 185, 129, 0.3);
  border-radius: 20px;
  color: #10b981;
  font-weight: 700;
  cursor: pointer;
}

.cost-details {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 0.5rem;
  padding: 1rem;
  background: rgba(0, 0, 0, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  min-width: 200px;
  z-index: 1000;
}

.cost-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  color: #ffffff;
}

.cost-savings {
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding-top: 0.5rem;
  color: #10b981;
  font-size: 0.875rem;
}
```

---

## 🚀 Running the Frontend

```bash
cd part3_frontend
npm install
npm run dev
```

Frontend will be available at: `http://localhost:3000`

---

## ✅ Success Criteria

✅ Chat interface functional  
✅ Aurora background animated  
✅ Real-time streaming works  
✅ Tool execution displayed  
✅ Cost tracking shown  
✅ Typing indicator animates  
✅ Message bubbles styled  
✅ Responsive design  
✅ Connects to Part 2 API  

---

## 📊 Expected Behavior

1. User opens chat → New session created
2. User types message → Sent to API
3. Agent responds → Streams in real-time
4. Tools execute → Displayed with icons
5. Cost updates → Shown in header
6. Conversation flows → Natural chat experience

---

**Build this and the Librarian Agent is complete!** 🎉

All 3 parts working together for the ultimate intelligent agent experience!
