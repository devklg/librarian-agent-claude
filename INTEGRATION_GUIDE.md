# Integration Guide

**How to connect all 3 parts of the Librarian Agent**

---

## 🎯 Goal

Connect:
1. Part 1 (Core Agent) ← Backend
2. Part 2 (API Layer) ← Middleware
3. Part 3 (Frontend) ← User Interface
4. Universal Memory Bridge ← Data storage

---

## 📁 Directory Structure

After building all 3 parts, your structure should be:

```
D:/librarian-agent-claude/
├── part1_core_agent/              ← Part 1 (Complete)
│   ├── librarian_claude_agent.py
│   ├── skill_manager.py
│   ├── agent_tools.py
│   ├── conversation_manager.py
│   └── requirements.txt
│
├── part2_api_layer/               ← Part 2 (To build)
│   ├── api.py
│   ├── websocket_handler.py
│   ├── session_manager.py
│   ├── bridge_connector.py
│   └── requirements.txt
│
├── part3_frontend/                ← Part 3 (To build)
│   ├── src/
│   │   ├── pages/AgentChat.jsx
│   │   ├── components/
│   │   └── services/agentService.js
│   ├── package.json
│   └── vite.config.js
│
└── README.md
```

---

## 🔗 Integration Steps

### Step 1: Part 2 Imports Part 1

**File**: `part2_api_layer/api.py`

```python
import sys
import os

# Add Part 1 to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../part1_core_agent'))

# Import the agent
from librarian_claude_agent import LibrarianClaudeAgent

# Initialize at startup
agent = None

@app.on_event("startup")
async def startup():
    global agent
    agent = LibrarianClaudeAgent()
    print("✅ Librarian Agent initialized")

# Use in endpoints
@app.post("/api/agent/chat/{session_id}")
async def send_message(session_id: str, request: MessageRequest):
    response = await agent.chat(
        message=request.message,
        session_id=session_id,
        requester_id=request.requester_id,
        requester_type=request.requester_type
    )
    return response
```

---

### Step 2: Part 2 Connects to Universal Memory Bridge

**File**: `part2_api_layer/bridge_connector.py`

```python
import sys
sys.path.append('/path/to/existing/librarian-agent')

from universal_memory_bridge import UniversalMemoryBridge

class BridgeConnector:
    def __init__(self):
        self.bridge = UniversalMemoryBridge()
        self.bridge.connect()
    
    def search(self, query, n_results=5):
        return self.bridge.query_knowledge(query, n_results)
    
    def store(self, module_data):
        return self.bridge.store_module(**module_data)
```

**Integration in Part 1**:

Update `part1_core_agent/agent_tools.py`:

```python
# In AgentTools class

def __init__(self):
    # Import bridge connector
    try:
        sys.path.append('../part2_api_layer')
        from bridge_connector import BridgeConnector
        self.bridge = BridgeConnector()
    except ImportError:
        print("⚠️  Bridge connector not found, using mock")
        self.bridge = None

async def search_documentation(self, query, category="all", n_results=5):
    if self.bridge:
        # Use real Universal Memory Bridge
        return self.bridge.search(query, n_results)
    else:
        # Return mock data
        return self._mock_search(query, n_results)
```

---

### Step 3: Part 3 Calls Part 2 API

**File**: `part3_frontend/src/services/agentService.js`

```javascript
const API_BASE = 'http://localhost:9600';

export async function createSession() {
  const response = await fetch(`${API_BASE}/api/agent/chat/new`, {
    method: 'POST'
  });
  return response.json();
}

export async function sendMessage(sessionId, message, callbacks) {
  const response = await fetch(
    `${API_BASE}/api/agent/chat/${sessionId}`, 
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message,
        requester_id: 'user',
        requester_type: 'human'
      })
    }
  );

  // Handle SSE stream
  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value);
    // Parse and call callbacks
    // ... (see PART3_FRONTEND_SPEC.md for full implementation)
  }
}
```

---

### Step 4: Configure Environment Variables

**Part 1 & Part 2**: Create `.env` file

```bash
# Claude API
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Universal Memory Bridge Databases
CHROMADB_URL=http://localhost:8000
MONGODB_URI=mongodb://localhost:29000
MONGODB_DATABASE=agent_command_center
NEO4J_URI=neo4j://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-password
NEON_CONNECTION_STRING=postgresql://user:pass@ep-xxx.aws.neon.tech/db

# API Configuration
API_HOST=0.0.0.0
API_PORT=9600
```

**Part 3**: Update `vite.config.js`

```javascript
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:9600',
        changeOrigin: true
      }
    }
  }
});
```

---

## 🚀 Startup Sequence

### Terminal 1: Universal Memory Bridge (Existing)
```bash
cd /path/to/existing/librarian-agent
python api.py
# Runs on port 9600 (or configure different port)
```

### Terminal 2: Part 2 API Layer
```bash
cd librarian-agent-claude/part2_api_layer
pip install -r requirements.txt
export ANTHROPIC_API_KEY="your-key"
uvicorn api:app --host 0.0.0.0 --port 9600 --reload
```

### Terminal 3: Part 3 Frontend
```bash
cd librarian-agent-claude/part3_frontend
npm install
npm run dev
# Opens at http://localhost:3000
```

---

## 🔍 Testing Integration

### 1. Test Part 1 Standalone

```python
# test_part1.py
from part1_core_agent.librarian_claude_agent import LibrarianClaudeAgent
import asyncio

async def test():
    agent = LibrarianClaudeAgent()
    response = await agent.chat(
        message="Hello!",
        session_id="test-123"
    )
    print(response)

asyncio.run(test())
```

### 2. Test Part 2 API

```bash
# Health check
curl http://localhost:9600/health

# Create session
curl -X POST http://localhost:9600/api/agent/chat/new

# Send message
curl -X POST http://localhost:9600/api/agent/chat/SESSION_ID \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!"}'
```

### 3. Test Part 3 Frontend

- Open http://localhost:3000
- Click "Agent Chat"
- Send a message
- Verify streaming works
- Check cost tracking updates

---

## 🐛 Troubleshooting

### "Module not found" errors

**Problem**: Parts can't import each other

**Solution**: Check sys.path additions

```python
import sys
import os

# Get absolute path to Part 1
part1_path = os.path.abspath(os.path.join(
    os.path.dirname(__file__), 
    '../part1_core_agent'
))
sys.path.insert(0, part1_path)
```

### "CORS policy" errors

**Problem**: Frontend can't connect to API

**Solution**: Add CORS in Part 2

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### "Database connection failed"

**Problem**: Can't connect to Universal Memory Bridge

**Solution**: Verify databases running

```bash
# Check ChromaDB
curl http://localhost:8000/api/v1/heartbeat

# Check MongoDB
mongosh --port 29000 --eval "db.adminCommand('ping')"

# Check Neo4j
curl http://localhost:7474

# Check Neon
psql $NEON_CONNECTION_STRING -c "SELECT 1"
```

### Skills not loading

**Problem**: "/mnt/skills not found"

**Solution**: Update skills path in Part 1

```python
# skill_manager.py
class SkillManager:
    def __init__(self, skills_base_path="/mnt/skills"):
        # Change to your actual path
        self.skills_base_path = skills_base_path
```

### High API costs

**Problem**: Cache not working

**Solution**: Check cache hits in logs

```python
# In Part 1, add logging
print(f"Cache Hit: {response.cache_hit}")
print(f"Cache Read Tokens: {response.usage.cache_read_tokens}")
```

---

## 📊 Verifying Integration Success

### ✅ Checklist

1. **Part 1** ← Part 2 imports work
2. **Part 2** ← API endpoints respond
3. **Part 3** ← Frontend loads
4. **Frontend** → API connection works
5. **API** → Agent responds
6. **Agent** → Claude SDK calls succeed
7. **Agent** → Skills load
8. **Agent** → Tools execute
9. **Bridge** → Database queries work
10. **Cache** → Cost savings visible

### Expected Flow

```
User types in frontend
  ↓
Frontend POST to /api/agent/chat/{session_id}
  ↓
API Layer receives request
  ↓
API calls agent.chat()
  ↓
Agent queries skills (cached!)
  ↓
Agent searches docs via bridge
  ↓
Agent calls Claude SDK (with caching)
  ↓
Claude responds with streaming
  ↓
API streams via SSE
  ↓
Frontend receives chunks
  ↓
User sees response + cost savings!
```

---

## 🎉 Integration Complete!

When all parts work together:
- ✅ Beautiful aurora UI
- ✅ Real-time chat streaming
- ✅ 90% cost savings from caching
- ✅ Expert skills guidance
- ✅ 4-database knowledge system
- ✅ Tool execution visible
- ✅ Conversation context maintained

---

## 📚 Additional Resources

- **Part 1 README**: `part1_core_agent/README.md`
- **Part 2 Specification**: `PART2_API_SPEC.md`
- **Part 3 Specification**: `PART3_FRONTEND_SPEC.md`
- **Main README**: `README.md`

---

**Need help? Check the troubleshooting section or create an issue on GitHub!**

Happy integrating! 🚀
