# Librarian Agent - Claude SDK Edition

**Intelligent knowledge keeper powered by Claude SDK with Prompt Caching, Skills, and Docling Multi-modal Processing**

🔗 **Repository**: https://github.com/devklg/librarian-agent-claude

---

## 🎯 Overview

The Librarian Agent is an intelligent AI agent that:
- **Manages knowledge** across 4 databases (ChromaDB, MongoDB, Neo4j, Neon)
- **Uses Claude SDK** for natural language understanding
- **Leverages Prompt Caching** for 90% cost savings
- **Integrates Skills** for expert guidance
- **Uses Docling** for multi-modal document processing (text + images!)
- **Provides chat interface** with beautiful Aurora background
- **Executes tools** to search, load, and organize documentation

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- Claude API key

### 1. Start Part 2 (API Layer)
```bash
cd part2_api_layer
pip install -r requirements.txt
export ANTHROPIC_API_KEY="your-key"
uvicorn api:app --port 9600 --reload
```

### 2. Start Part 3 (Frontend)
```bash
cd part3_frontend
npm install
npm run dev
```

### 3. Open Browser
Navigate to: `http://localhost:3000`

---

## 📊 Cost Savings with Prompt Caching

**Without Caching**: $0.0195 per query
**With Caching**: $0.0022 per query (88.7% savings!)

---

**Built with ❤️ using Claude SDK, Skills, and Prompt Caching**
