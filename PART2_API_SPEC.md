# Part 2: API Layer Specification

**RESTful API with WebSocket support for Librarian Claude Agent**

---

## 🎯 Your Mission

Build a FastAPI application that exposes the Librarian Claude Agent (Part 1) to external clients (Part 3 frontend, other agents, applications).

---

## 📋 Requirements

### Technology Stack
- **Framework**: FastAPI 0.104+
- **WebSocket**: For real-time streaming
- **CORS**: Enable cross-origin requests
- **Session Management**: Track conversation sessions
- **Database Integration**: Connect Part 1 to Universal Memory Bridge

### What You're Building

```
part2_api_layer/
├── api.py                    # Main FastAPI application
├── websocket_handler.py      # WebSocket streaming
├── session_manager.py        # Session tracking
├── bridge_connector.py       # Connect to Universal Memory Bridge
├── requirements.txt          # Dependencies
└── README.md                 # Setup guide
```

---

## 🔌 Integration Points

### Import from Part 1

```python
import sys
sys.path.append('../part1_core_agent')

from librarian_claude_agent import LibrarianClaudeAgent
```

### Connect to Universal Memory Bridge

```python
# Add existing Universal Memory Bridge
sys.path.append('/path/to/existing/librarian-agent')

from universal_memory_bridge import UniversalMemoryBridge
```

---

## 📡 API Endpoints to Build

### 1. Health Check

```python
@app.get("/health")
async def health_check():
    """
    Check API and agent health
    
    Returns:
        {
            "status": "healthy",
            "agent_ready": true,
            "databases": {
                "chromadb": "healthy",
                "mongodb": "healthy",
                "neo4j": "healthy",
                "neon": "healthy"
            }
        }
    """
```

### 2. Start New Conversation

```python
@app.post("/api/agent/chat/new")
async def new_conversation():
    """
    Create a new conversation session
    
    Returns:
        {
            "session_id": "uuid-here",
            "created_at": "2025-11-25T16:00:00Z"
        }
    """
```

### 3. Send Message (Streaming)

```python
@app.post("/api/agent/chat/{session_id}")
async def send_message(session_id: str, request: MessageRequest):
    """
    Send message and get streaming response
    
    Request Body:
        {
            "message": "User's question",
            "requester_id": "user-123",
            "requester_type": "human"
        }
    
    Returns: Server-Sent Events (SSE) stream
        event: message_start
        data: {"session_id": "..."}
        
        event: content
        data: {"text": "Here's how..."}
        
        event: tool_call
        data: {"name": "search_documentation", "input": {...}}
        
        event: message_end
        data: {"cost": {...}, "usage": {...}}
    """
```

### 4. Get Conversation History

```python
@app.get("/api/agent/chat/{session_id}/history")
async def get_history(session_id: str):
    """
    Get full conversation history
    
    Returns:
        {
            "session_id": "...",
            "turns": [
                {
                    "timestamp": "...",
                    "user_message": "...",
                    "agent_response": "...",
                    "skills_used": ["pptx"],
                    "tool_calls": [...]
                }
            ],
            "stats": {
                "total_turns": 5,
                "total_cost": 0.05,
                "cache_hits": 4
            }
        }
    """
```

### 5. Get Session Stats

```python
@app.get("/api/agent/chat/{session_id}/stats")
async def get_stats(session_id: str):
    """
    Get session statistics
    
    Returns:
        {
            "session_id": "...",
            "total_turns": 5,
            "total_tools_used": 3,
            "unique_skills_used": ["pptx", "docx"],
            "session_duration_seconds": 300,
            "total_cost": 0.05,
            "total_savings": 0.15,
            "cache_hit_rate": 0.80
        }
    """
```

### 6. List Active Sessions

```python
@app.get("/api/agent/sessions")
async def list_sessions():
    """
    List all active sessions
    
    Returns:
        {
            "active_sessions": 10,
            "sessions": [
                {
                    "session_id": "...",
                    "started_at": "...",
                    "last_activity": "...",
                    "turn_count": 5
                }
            ]
        }
    """
```

### 7. WebSocket Endpoint

```python
@app.websocket("/ws/agent/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket for real-time bi-directional communication
    
    Client sends:
        {
            "type": "message",
            "content": "User's question"
        }
    
    Server streams:
        {
            "type": "start",
            "session_id": "..."
        }
        {
            "type": "content",
            "text": "Here's how..."
        }
        {
            "type": "end",
            "cost": {...}
        }
    """
```

---

## 📝 Pydantic Models

```python
from pydantic import BaseModel
from typing import List, Dict, Optional

class MessageRequest(BaseModel):
    message: str
    requester_id: str = "user"
    requester_type: str = "human"

class MessageResponse(BaseModel):
    session_id: str
    message: str
    tool_calls: List[Dict]
    skills_used: List[str]
    cost: Dict
    usage: Dict
    response_time: float
    cache_hit: bool

class ConversationTurn(BaseModel):
    timestamp: float
    user_message: str
    agent_response: str
    tool_calls: List[Dict]
    skills_used: List[str]

class SessionStats(BaseModel):
    session_id: str
    total_turns: int
    total_tools_used: int
    unique_skills_used: List[str]
    session_duration_seconds: float
    total_cost: float
    total_savings: float
    cache_hit_rate: float
```

---

## 🔥 Server-Sent Events (SSE) Implementation

For streaming responses:

```python
from fastapi.responses import StreamingResponse
import json

async def generate_sse(agent_response):
    """Generate Server-Sent Events stream"""
    
    # Start event
    yield f"event: message_start\ndata: {json.dumps({'session_id': '...'})}\n\n"
    
    # Stream content (could come from Claude streaming)
    for chunk in agent_response['message'].split():
        yield f"event: content\ndata: {json.dumps({'text': chunk + ' '})}\n\n"
        await asyncio.sleep(0.05)  # Simulate streaming
    
    # Tool calls
    for tool in agent_response.get('tool_calls', []):
        yield f"event: tool_call\ndata: {json.dumps(tool)}\n\n"
    
    # End event
    yield f"event: message_end\ndata: {json.dumps({'cost': agent_response['cost']})}\n\n"

@app.post("/api/agent/chat/{session_id}")
async def send_message(session_id: str, request: MessageRequest):
    response = await agent.chat(
        message=request.message,
        session_id=session_id
    )
    
    return StreamingResponse(
        generate_sse(response),
        media_type="text/event-stream"
    )
```

---

## 🗄️ Session Management

```python
# session_manager.py

import uuid
from datetime import datetime
from typing import Dict, List

class SessionManager:
    def __init__(self):
        self.sessions = {}  # session_id -> session_info
    
    def create_session(self) -> str:
        """Create new session"""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "session_id": session_id,
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow(),
            "turn_count": 0
        }
        return session_id
    
    def update_activity(self, session_id: str):
        """Update last activity time"""
        if session_id in self.sessions:
            self.sessions[session_id]["last_activity"] = datetime.utcnow()
            self.sessions[session_id]["turn_count"] += 1
    
    def get_session_info(self, session_id: str) -> Dict:
        """Get session information"""
        return self.sessions.get(session_id, {})
    
    def list_active_sessions(self) -> List[Dict]:
        """List all active sessions"""
        return list(self.sessions.values())
    
    def cleanup_old_sessions(self, max_age_minutes: int = 60):
        """Remove sessions older than max_age_minutes"""
        # Implementation here
        pass
```

---

## 🌉 Bridge Connector

```python
# bridge_connector.py

class BridgeConnector:
    """
    Connects the agent to the existing Universal Memory Bridge
    """
    
    def __init__(self):
        # Import existing Universal Memory Bridge
        from universal_memory_bridge import UniversalMemoryBridge
        self.bridge = UniversalMemoryBridge()
        self.bridge.connect()
    
    def search(self, query: str, n_results: int = 5):
        """Search the knowledge base"""
        return self.bridge.query_knowledge(query, n_results=n_results)
    
    def store(self, module_data: dict):
        """Store new knowledge module"""
        return self.bridge.store_module(**module_data)
    
    def get_health(self):
        """Check database health"""
        return self.bridge.get_health_status()
```

---

## 🚀 Main Application

```python
# api.py

from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import sys

# Import Part 1
sys.path.append('../part1_core_agent')
from librarian_claude_agent import LibrarianClaudeAgent

# Import components
from session_manager import SessionManager
from bridge_connector import BridgeConnector
from websocket_handler import WebSocketHandler

# Initialize
app = FastAPI(title="Librarian Agent API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
agent = None
session_manager = SessionManager()
bridge_connector = None
ws_handler = WebSocketHandler()

@app.on_event("startup")
async def startup():
    """Initialize on startup"""
    global agent, bridge_connector
    
    # Initialize agent
    agent = LibrarianClaudeAgent()
    
    # Connect to Universal Memory Bridge
    bridge_connector = BridgeConnector()
    
    print("✅ Librarian Agent API ready")

@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    print("👋 Shutting down...")

# Implement all endpoints here...
```

---

## 📦 Dependencies

```
# requirements.txt

fastapi==0.104.1
uvicorn[standard]==0.24.0
websockets==12.0
python-multipart==0.0.6
pydantic==2.5.0
aiohttp==3.9.0
```

---

## 🧪 Testing

Create test file:

```python
# test_api.py

import requests

BASE_URL = "http://localhost:9600"

def test_health():
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_new_session():
    response = requests.post(f"{BASE_URL}/api/agent/chat/new")
    assert response.status_code == 200
    assert "session_id" in response.json()
    return response.json()["session_id"]

def test_send_message():
    session_id = test_new_session()
    response = requests.post(
        f"{BASE_URL}/api/agent/chat/{session_id}",
        json={"message": "Hello!"}
    )
    assert response.status_code == 200
```

---

## 🎯 Success Criteria

✅ All 7 endpoints implemented  
✅ SSE streaming works  
✅ WebSocket connection stable  
✅ Session management functional  
✅ Connects to Part 1 agent  
✅ Connects to Universal Memory Bridge  
✅ CORS properly configured  
✅ Error handling throughout  
✅ Tests pass  

---

## 🚀 Running the API

```bash
cd part2_api_layer
pip install -r requirements.txt
uvicorn api:app --host 0.0.0.0 --port 9600 --reload
```

API will be available at: `http://localhost:9600`

---

## 📊 Expected Performance

- **Response Time**: 2-4 seconds per message
- **Streaming Latency**: <100ms per chunk
- **Concurrent Sessions**: 100+ supported
- **WebSocket Connections**: 50+ simultaneous

---

## 🔌 Integration with Part 3

Part 3 (Frontend) will call these endpoints:

```javascript
// Create session
const { session_id } = await fetch('http://localhost:9600/api/agent/chat/new', {
  method: 'POST'
}).then(r => r.json());

// Stream messages
const eventSource = new EventSource(
  `http://localhost:9600/api/agent/chat/${session_id}`,
  { method: 'POST', body: JSON.stringify({ message: "Hello!" }) }
);

eventSource.addEventListener('content', (e) => {
  const data = JSON.parse(e.data);
  console.log(data.text);
});
```

---

**Build this and you're 1/3 done!** 🚀

When complete, Part 3 can connect to your API for the frontend.
