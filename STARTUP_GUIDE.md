# 🚀 Librarian Agent - Startup Guide

Complete guide to running the Librarian Agent locally or with Docker.

---

## 📋 Prerequisites

- **Python 3.9+** (for local setup)
- **Node.js 18+** (for local setup)
- **Docker & Docker Compose** (for Docker setup)
- **Anthropic API Key** (for production mode)

---

## 🎯 Quick Start (3 Methods)

### Method 1: Local Development (Recommended for Development)

#### Step 1: Set Up Environment

```bash
# Clone the repository (if not already done)
git clone https://github.com/devklg/librarian-agent-claude.git
cd librarian-agent-claude

# Create .env file
cp .env.example .env

# Edit .env and add your API key
nano .env  # or use your favorite editor
```

**Add to .env:**
```bash
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

#### Step 2: Start API Server (Terminal 1)

```bash
# Navigate to API directory
cd part2_api_layer

# Install dependencies
pip install -r requirements.txt

# Start the API server
uvicorn api:app --host 0.0.0.0 --port 9600 --reload
```

You should see:
```
🚀 Starting Librarian Agent API...
✅ Librarian Agent initialized successfully
✅ Librarian Agent API ready on http://localhost:9600
INFO:     Uvicorn running on http://0.0.0.0:9600
```

#### Step 3: Start Frontend (Terminal 2)

```bash
# Navigate to frontend directory
cd part3_frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

You should see:
```
VITE v5.4.21 ready in 485 ms
➜  Local:   http://localhost:3000/
```

#### Step 4: Open Browser

Navigate to: **http://localhost:3000**

---

### Method 2: Docker Compose (Recommended for Production)

#### Step 1: Prepare Environment

```bash
# Create .env file
cp .env.example .env

# Add your API key
echo "ANTHROPIC_API_KEY=sk-ant-your-key-here" >> .env
```

#### Step 2: Build and Start Services

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

#### Step 3: Access the Application

- **Frontend:** http://localhost:3000
- **API:** http://localhost:9600
- **API Docs:** http://localhost:9600/docs

#### Step 4: View Logs

```bash
# View all logs
docker-compose logs -f

# View API logs only
docker-compose logs -f api

# View frontend logs only
docker-compose logs -f frontend
```

#### Step 5: Stop Services

```bash
# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

---

### Method 3: Docker Manual (Advanced)

#### Build Images

```bash
# Build API image
docker build -f Dockerfile.api -t librarian-agent-api .

# Build Frontend image
docker build -f part3_frontend/Dockerfile -t librarian-agent-frontend ./part3_frontend
```

#### Run Containers

```bash
# Run API container
docker run -d \
  --name librarian-api \
  -p 9600:9600 \
  -e ANTHROPIC_API_KEY=sk-ant-your-key-here \
  librarian-agent-api

# Run Frontend container
docker run -d \
  --name librarian-frontend \
  -p 3000:3000 \
  --link librarian-api:api \
  librarian-agent-frontend
```

---

## 🧪 Testing the Setup

### 1. Check API Health

```bash
curl http://localhost:9600/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "agent_ready": true,
  "agent_mode": "production",
  "api_key_configured": true,
  "active_sessions": 0,
  "timestamp": "2025-12-19T23:31:53.966528"
}
```

### 2. Create a Test Session

```bash
curl -X POST http://localhost:9600/api/agent/chat/new
```

**Expected Response:**
```json
{
  "session_id": "uuid-here",
  "created_at": "2025-12-19T23:32:31.961812",
  "status": "created"
}
```

### 3. Test Frontend

Open http://localhost:3000 in your browser. You should see:
- Beautiful Aurora background animation
- "Librarian Agent" header
- Chat input box at the bottom
- "Powered by Claude SDK" subtitle

---

## 🔧 Configuration Options

### API Configuration (part2_api_layer/)

**Environment Variables:**
```bash
ANTHROPIC_API_KEY=sk-ant-...    # Required for production mode
API_HOST=0.0.0.0                # API host (default: 0.0.0.0)
API_PORT=9600                   # API port (default: 9600)
```

**Running with custom port:**
```bash
cd part2_api_layer
API_PORT=8000 uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Configuration (part3_frontend/)

**vite.config.js** - Proxy configuration:
```javascript
export default {
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': 'http://localhost:9600',  // Change if API port differs
      '/ws': {
        target: 'ws://localhost:9600',
        ws: true
      }
    }
  }
}
```

---

## 🐛 Troubleshooting

### Issue: API Key Not Working

**Check:**
```bash
echo $ANTHROPIC_API_KEY
```

**Solution:**
```bash
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
```

### Issue: Port Already in Use

**Check what's using the port:**
```bash
# Linux/Mac
lsof -i :9600
lsof -i :3000

# Windows
netstat -ano | findstr :9600
netstat -ano | findstr :3000
```

**Solution: Kill the process or use different port:**
```bash
# Use different API port
cd part2_api_layer
uvicorn api:app --host 0.0.0.0 --port 9601 --reload

# Use different frontend port
cd part3_frontend
npm run dev -- --port 3001
```

### Issue: Module Not Found Errors

**Solution: Reinstall dependencies:**
```bash
# API
cd part2_api_layer
pip install -r requirements.txt --force-reinstall

# Frontend
cd part3_frontend
rm -rf node_modules package-lock.json
npm install
```

### Issue: CORS Errors

**Check API CORS configuration in `api.py`:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: Docker Build Fails

**Solution: Clear Docker cache:**
```bash
docker-compose down -v
docker system prune -a
docker-compose up --build
```

---

## 📊 Development vs Production

### Development Mode (No API Key)

The application runs in **mock mode** when no API key is configured:
- ✅ All endpoints work
- ✅ Sessions created
- ✅ Mock responses returned
- ❌ No actual Claude API calls
- ❌ No real tool execution

**Good for:**
- Frontend development
- API testing
- UI/UX work
- Demo purposes

### Production Mode (With API Key)

Full functionality with Claude SDK:
- ✅ Real Claude API integration
- ✅ Prompt caching (90% cost savings)
- ✅ Skills integration
- ✅ Tool execution
- ✅ Multi-database search
- ✅ Document processing

**Required for:**
- Production deployment
- Real conversations
- Knowledge base queries
- Document analysis

---

## 🔍 API Endpoints Reference

### REST Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/` | API info |
| POST | `/api/agent/chat/new` | Create new session |
| POST | `/api/agent/chat/{session_id}` | Send message (SSE stream) |
| GET | `/api/agent/chat/{session_id}/history` | Get conversation history |
| GET | `/api/agent/chat/{session_id}/stats` | Get session statistics |
| GET | `/api/agent/sessions` | List all active sessions |
| DELETE | `/api/agent/chat/{session_id}` | Delete session |

### WebSocket Endpoint

| Protocol | Endpoint | Description |
|----------|----------|-------------|
| WS | `/ws/agent/{session_id}` | Real-time bidirectional chat |

### Interactive API Docs

Visit: **http://localhost:9600/docs**

Swagger UI with:
- All endpoints documented
- Try it out functionality
- Request/response schemas
- Example payloads

---

## 📁 Project Structure

```
librarian-agent-claude/
├── part1_core_agent/           # Core Agent Engine
│   ├── librarian_claude_agent.py
│   ├── skill_manager.py
│   ├── agent_tools.py
│   ├── conversation_manager.py
│   ├── docling_extractor.py
│   └── requirements.txt
│
├── part2_api_layer/            # API Layer (FastAPI)
│   ├── api.py                  # Main FastAPI app
│   ├── session_manager.py      # Session management
│   ├── websocket_handler.py    # WebSocket handler
│   ├── bridge_connector.py     # Database bridge
│   └── requirements.txt
│
├── part3_frontend/             # Frontend (React + Vite)
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   ├── pages/AgentChat.jsx
│   │   ├── services/agentService.js
│   │   └── styles/AgentChat.css
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile
│
├── docker-compose.yml          # Docker Compose config
├── Dockerfile.api              # API Dockerfile
├── .env.example                # Environment template
├── STARTUP_GUIDE.md           # This file
└── README.md                   # Project overview
```

---

## 🚀 Production Deployment

### Using Docker Compose (Recommended)

1. **Set up production environment:**
```bash
cp .env.example .env
# Add production API key and configs
```

2. **Build production images:**
```bash
docker-compose build
```

3. **Start services:**
```bash
docker-compose up -d
```

4. **Set up reverse proxy (nginx example):**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api {
        proxy_pass http://localhost:9600;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /ws {
        proxy_pass http://localhost:9600;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
    }
}
```

5. **Monitor logs:**
```bash
docker-compose logs -f
```

---

## 📞 Support

- **Documentation:** See `README.md`, `INTEGRATION_GUIDE.md`
- **API Spec:** See `PART2_API_SPEC.md`
- **Issues:** https://github.com/devklg/librarian-agent-claude/issues

---

## ✅ Checklist

### Before Starting:
- [ ] Python 3.9+ installed (for local)
- [ ] Node.js 18+ installed (for local)
- [ ] Docker installed (for Docker setup)
- [ ] API key obtained from Anthropic
- [ ] `.env` file created with API key

### After Starting:
- [ ] API responds at http://localhost:9600/health
- [ ] Frontend loads at http://localhost:3000
- [ ] Can create new sessions
- [ ] Can send messages and receive responses
- [ ] No errors in browser console
- [ ] No errors in API logs

---

**You're all set! Enjoy using the Librarian Agent! 🎉**
