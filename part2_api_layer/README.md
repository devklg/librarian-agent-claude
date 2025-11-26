# Part 2: API Layer

FastAPI REST API with SSE streaming and WebSocket support.

## Features
- 7 REST endpoints
- SSE streaming
- WebSocket support
- Session management
- Bridge connector

## Start
```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY="your-key"
uvicorn api:app --port 9600 --reload
```

API: http://localhost:9600
