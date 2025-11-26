# Setup Guide

## Quick Start (5 minutes)

```bash
# Terminal 1: API
cd part2_api_layer
pip install -r requirements.txt
export ANTHROPIC_API_KEY="your-key"
uvicorn api:app --port 9600 --reload

# Terminal 2: Frontend
cd part3_frontend
npm install
npm run dev
```

Open http://localhost:3000

## Docker

```bash
docker-compose up --build
```

## Testing

```bash
curl http://localhost:9600/health
```
