# ⚡ Librarian Agent - Quick Start Reference

**Choose your preferred method:**

---

## 🎯 Method 1: Local Development (Fastest)

### Setup (One-time)
```bash
# Set API key
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
```

### Run (Every time)
```bash
# Terminal 1: API
cd part2_api_layer
pip install -r requirements.txt
uvicorn api:app --port 9600 --reload

# Terminal 2: Frontend  
cd part3_frontend
npm install
npm run dev
```

### Access
- **Frontend:** http://localhost:3000
- **API:** http://localhost:9600
- **Docs:** http://localhost:9600/docs

---

## 🐳 Method 2: Docker Compose (Production)

### Setup (One-time)
```bash
# Create .env file
echo "ANTHROPIC_API_KEY=sk-ant-your-key-here" > .env
```

### Run
```bash
# Start everything
docker-compose up --build

# Or in background
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Access
- **Frontend:** http://localhost:3000
- **API:** http://localhost:9600
- **Docs:** http://localhost:9600/docs

---

## 🧪 Test It Works

```bash
# Health check
curl http://localhost:9600/health

# Create session
curl -X POST http://localhost:9600/api/agent/chat/new

# Open frontend
open http://localhost:3000
```

---

## 📝 Files You Have Now

✅ **Docker Files:**
- `Dockerfile.api` - API container
- `part3_frontend/Dockerfile` - Frontend container  
- `docker-compose.yml` - Orchestration

✅ **Documentation:**
- `STARTUP_GUIDE.md` - Full detailed guide
- `ANALYSIS_AND_FIX.md` - What was fixed
- `QUICK_START.md` - This file
- `README.md` - Project overview

✅ **Configuration:**
- `.env.example` - Environment template

---

## 🆘 Quick Troubleshooting

**API won't start?**
```bash
# Check port availability
lsof -i :9600
# Kill if needed, or use different port
uvicorn api:app --port 9601 --reload
```

**Frontend won't start?**
```bash
# Check port availability
lsof -i :3000
# Kill if needed, or use different port
npm run dev -- --port 3001
```

**Docker issues?**
```bash
# Clean everything
docker-compose down -v
docker system prune -a
# Rebuild
docker-compose up --build
```

**Missing API key?**
```bash
# The app works in "mock mode" without an API key
# To get full features, get your key from:
# https://console.anthropic.com/
```

---

## 📊 What You Get

### Without API Key (Mock Mode)
- ✅ UI works
- ✅ Sessions work
- ✅ Mock responses
- ❌ No real Claude AI

### With API Key (Production)
- ✅ Real Claude AI
- ✅ Prompt caching (90% savings)
- ✅ Skills & tools
- ✅ Knowledge base
- ✅ Document processing

---

## 🔗 Important URLs

- **Pull Request:** https://github.com/devklg/librarian-agent-claude/pull/1
- **Repository:** https://github.com/devklg/librarian-agent-claude
- **Full Guide:** See `STARTUP_GUIDE.md`

---

**That's it! Pick a method and start! 🚀**
