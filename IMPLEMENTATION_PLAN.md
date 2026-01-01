# Librarian Agent - Implementation Plan

## Overview

This document outlines a structured implementation plan to transform the Librarian Agent from MVP to a top-tier production-ready tool. The plan is organized into 4 phases over multiple development cycles.

---

## Phase 1: Foundation & Critical Fixes

**Goal**: Fix breaking issues and establish development infrastructure

### 1.1 Fix Critical Bugs

#### 1.1.1 Fix Async Bug in API Layer
**File**: `part2_api_layer/api.py:167-171`

**Current (Broken)**:
```python
response = await asyncio.to_thread(
    agent_instance.chat,
    message=message,
    session_id=session_id
)
```

**Fixed**:
```python
response = await agent_instance.chat(
    message=message,
    session_id=session_id
)
```

**Impact**: Currently the async/await chain is broken, causing potential issues with event loop.

#### 1.1.2 Fix Missing Method in Agent
**File**: `part2_api_layer/api.py:147`

The API calls `agent.start_conversation(session_id)` but this method doesn't exist in `LibrarianClaudeAgent`.

**Fix**: Add the missing method or remove the call.

---

### 1.2 Testing Infrastructure

#### 1.2.1 Backend Tests (pytest)

**Directory Structure**:
```
tests/
├── __init__.py
├── conftest.py                 # Shared fixtures
├── unit/
│   ├── __init__.py
│   ├── test_librarian_agent.py
│   ├── test_skill_manager.py
│   ├── test_conversation_manager.py
│   ├── test_agent_tools.py
│   └── test_session_manager.py
├── integration/
│   ├── __init__.py
│   ├── test_api_endpoints.py
│   ├── test_sse_streaming.py
│   └── test_websocket.py
└── e2e/
    ├── __init__.py
    └── test_chat_flow.py
```

**Key Test Cases**:

| Component | Test Cases |
|-----------|------------|
| `LibrarianClaudeAgent` | Init, chat flow, skill detection, caching, cost calculation |
| `SkillManager` | Load skills, detect skills, search skills, handle missing files |
| `ConversationManager` | Add turns, get history, cache TTL, cleanup, stats |
| `AgentTools` | Each tool execution, error handling, mock responses |
| `API Endpoints` | All REST endpoints, error responses, validation |
| `SSE Streaming` | Event types, chunking, error events, connection handling |
| `WebSocket` | Connect, disconnect, message handling, broadcasting |

**Dependencies to Add**:
```
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0
httpx>=0.25.0  # For async API testing
pytest-mock>=3.12.0
```

#### 1.2.2 Frontend Tests (Vitest + Testing Library)

**Directory Structure**:
```
part3_frontend/
├── src/
│   ├── __tests__/
│   │   ├── AgentChat.test.jsx
│   │   └── agentService.test.js
```

**Dependencies to Add**:
```json
{
  "devDependencies": {
    "@testing-library/react": "^14.0.0",
    "@testing-library/jest-dom": "^6.0.0",
    "vitest": "^1.0.0",
    "jsdom": "^22.0.0"
  }
}
```

#### 1.2.3 CI/CD Pipeline

**File**: `.github/workflows/ci.yml`

```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r part1_core_agent/requirements.txt
          pip install -r part2_api_layer/requirements.txt
          pip install pytest pytest-asyncio pytest-cov httpx
      - name: Run tests
        run: pytest tests/ --cov=. --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - name: Install dependencies
        run: cd part3_frontend && npm ci
      - name: Run tests
        run: cd part3_frontend && npm test

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - name: Run ruff
        run: pip install ruff && ruff check .
      - name: Run mypy
        run: pip install mypy && mypy part1_core_agent/ part2_api_layer/
```

---

### 1.3 Configuration Management

#### 1.3.1 Create Settings Module

**File**: `part1_core_agent/config.py`

```python
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Keys
    anthropic_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None

    # Model Configuration
    model_id: str = "claude-sonnet-4-20250514"
    max_tokens: int = 4000

    # Caching
    cache_ttl_seconds: int = 300
    session_max_age_seconds: int = 3600

    # API Server
    api_host: str = "0.0.0.0"
    api_port: int = 9600

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    # Security
    cors_origins: list[str] = ["http://localhost:3000"]

    # Database URLs (for Phase 2)
    chromadb_url: Optional[str] = None
    mongodb_url: Optional[str] = None
    neo4j_url: Optional[str] = None
    neon_url: Optional[str] = None

    # Skills
    skills_base_path: str = "./skills"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

#### 1.3.2 Create Environment Files

**File**: `.env.example`
```env
# Required
ANTHROPIC_API_KEY=sk-ant-...

# Optional
OPENAI_API_KEY=sk-...

# Model
MODEL_ID=claude-sonnet-4-20250514
MAX_TOKENS=4000

# Server
API_HOST=0.0.0.0
API_PORT=9600

# Security
CORS_ORIGINS=["http://localhost:3000"]

# Logging
LOG_LEVEL=INFO
```

---

### 1.4 Logging Infrastructure

#### 1.4.1 Structured Logging Setup

**File**: `part1_core_agent/logging_config.py`

```python
import structlog
import logging
import sys

def configure_logging(log_level: str = "INFO", log_format: str = "json"):
    """Configure structured logging for the application"""

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )

    # Configure structlog
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    if log_format == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level.upper())
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

def get_logger(name: str = None):
    """Get a logger instance"""
    return structlog.get_logger(name)
```

**Usage in code**:
```python
from logging_config import get_logger

logger = get_logger(__name__)

# Replace print statements
logger.info("agent_initialized", skills_count=len(self.skills))
logger.error("chat_failed", error=str(e), session_id=session_id)
logger.warning("cache_miss", session_id=session_id, key="docs")
```

---

### 1.5 Create Actual Skills Files

#### 1.5.1 Skills Directory Structure

```
skills/
├── public/
│   ├── docx/
│   │   └── SKILL.md
│   ├── pptx/
│   │   └── SKILL.md
│   ├── xlsx/
│   │   └── SKILL.md
│   ├── pdf/
│   │   └── SKILL.md
│   ├── frontend-design/
│   │   └── SKILL.md
│   └── product-self-knowledge/
│       └── SKILL.md
└── examples/
    ├── skill-creator/
    │   └── SKILL.md
    ├── theme-factory/
    │   └── SKILL.md
    └── brand-guidelines/
        └── SKILL.md
```

#### 1.5.2 Example Skill Content

**File**: `skills/public/docx/SKILL.md`

```markdown
# DOCX Skill - Word Document Expert

## Purpose
Guide for creating and editing Microsoft Word documents programmatically.

## Capabilities
- Create new documents with proper structure
- Add headings, paragraphs, tables, and lists
- Insert images and charts
- Apply styles and formatting
- Create headers/footers and page numbers
- Generate table of contents

## Best Practices

### Document Structure
1. Always start with a title (Heading 1)
2. Use proper heading hierarchy (H1 > H2 > H3)
3. Include page numbers for documents > 3 pages
4. Add a table of contents for documents > 10 pages

### Formatting
- Use consistent fonts (recommended: Calibri, Arial)
- Body text: 11-12pt
- Headings: 14-18pt depending on level
- Line spacing: 1.15 or 1.5 for readability
- Margins: 1 inch on all sides (standard)

### Tables
- Include header row with bold text
- Use alternating row colors for readability
- Keep tables on single page when possible

## Code Examples

### Python (python-docx)
```python
from docx import Document
from docx.shared import Inches, Pt

doc = Document()
doc.add_heading('Document Title', 0)
doc.add_paragraph('This is a paragraph.')
doc.add_table(rows=3, cols=3)
doc.save('output.docx')
```

## Common Issues
- Large images can bloat file size (compress first)
- Complex tables may not render correctly in all viewers
- Fonts must be available on the viewing system
```

---

## Phase 2: Security & Database Integration

**Goal**: Implement authentication and connect real databases

### 2.1 Authentication System

#### 2.1.1 JWT Authentication

**File**: `part2_api_layer/auth.py`

```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

# Configuration
SECRET_KEY = "your-secret-key"  # Load from settings
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[str] = None

class User(BaseModel):
    id: str
    email: str
    is_active: bool = True

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Fetch user from database (implement this)
    user = await get_user_by_id(user_id)
    if user is None:
        raise credentials_exception
    return user
```

#### 2.1.2 Protected Endpoints

```python
from auth import get_current_user, User

@app.post("/api/agent/chat/{session_id}")
async def send_message(
    session_id: str,
    request: MessageRequest,
    current_user: User = Depends(get_current_user)  # Added
):
    # Verify user owns this session
    session = session_manager.get_session_info(session_id)
    if session.get("user_id") != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    ...
```

#### 2.1.3 API Key Authentication (Alternative)

```python
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Depends(api_key_header)):
    # Validate API key against database
    if not await is_valid_api_key(api_key):
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key
```

---

### 2.2 Rate Limiting

**File**: `part2_api_layer/rate_limit.py`

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)

# In api.py
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/agent/chat/{session_id}")
@limiter.limit("10/minute")  # 10 requests per minute
async def send_message(...):
    ...
```

---

### 2.3 Database Integrations

#### 2.3.1 ChromaDB Integration (Vector Search)

**File**: `part1_core_agent/databases/chromadb_client.py`

```python
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any

class ChromaDBClient:
    def __init__(self, host: str = "localhost", port: int = 8000):
        self.client = chromadb.HttpClient(
            host=host,
            port=port,
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_or_create_collection(
            name="documentation",
            metadata={"hnsw:space": "cosine"}
        )

    async def search(
        self,
        query: str,
        n_results: int = 5,
        where: Dict = None
    ) -> List[Dict[str, Any]]:
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where
        )
        return self._format_results(results)

    async def add_documents(
        self,
        documents: List[str],
        metadatas: List[Dict],
        ids: List[str]
    ):
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

    def _format_results(self, results) -> List[Dict[str, Any]]:
        formatted = []
        for i, doc in enumerate(results['documents'][0]):
            formatted.append({
                'content': doc,
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i] if results.get('distances') else None
            })
        return formatted
```

#### 2.3.2 MongoDB Integration (Document Storage)

**File**: `part1_core_agent/databases/mongodb_client.py`

```python
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Dict, Any, Optional

class MongoDBClient:
    def __init__(self, url: str):
        self.client = AsyncIOMotorClient(url)
        self.db = self.client.librarian
        self.documents = self.db.documents
        self.sessions = self.db.sessions

    async def store_document(self, document: Dict[str, Any]) -> str:
        result = await self.documents.insert_one(document)
        return str(result.inserted_id)

    async def get_document(self, doc_id: str) -> Optional[Dict]:
        return await self.documents.find_one({"_id": doc_id})

    async def search_documents(
        self,
        query: Dict,
        limit: int = 10
    ) -> List[Dict]:
        cursor = self.documents.find(query).limit(limit)
        return await cursor.to_list(length=limit)

    async def store_session(self, session_id: str, data: Dict):
        await self.sessions.update_one(
            {"session_id": session_id},
            {"$set": data},
            upsert=True
        )
```

#### 2.3.3 Neo4j Integration (Knowledge Graph)

**File**: `part1_core_agent/databases/neo4j_client.py`

```python
from neo4j import AsyncGraphDatabase
from typing import List, Dict, Any

class Neo4jClient:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = AsyncGraphDatabase.driver(uri, auth=(user, password))

    async def close(self):
        await self.driver.close()

    async def add_relationship(
        self,
        source: str,
        target: str,
        relationship: str,
        properties: Dict = None
    ):
        query = """
        MERGE (a:Entity {name: $source})
        MERGE (b:Entity {name: $target})
        MERGE (a)-[r:RELATES {type: $rel_type}]->(b)
        SET r += $properties
        RETURN a, r, b
        """
        async with self.driver.session() as session:
            await session.run(
                query,
                source=source,
                target=target,
                rel_type=relationship,
                properties=properties or {}
            )

    async def query_relationships(
        self,
        entity: str,
        depth: int = 2
    ) -> List[Dict]:
        query = """
        MATCH path = (e:Entity {name: $entity})-[*1..$depth]-(related)
        RETURN path
        """
        async with self.driver.session() as session:
            result = await session.run(query, entity=entity, depth=depth)
            return await result.data()
```

#### 2.3.4 PostgreSQL/Neon Integration (SQL)

**File**: `part1_core_agent/databases/postgres_client.py`

```python
import asyncpg
from typing import List, Dict, Any, Optional

class PostgresClient:
    def __init__(self, url: str):
        self.url = url
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(self.url)

    async def close(self):
        if self.pool:
            await self.pool.close()

    async def execute(self, query: str, *args) -> str:
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)

    async def fetch(self, query: str, *args) -> List[Dict]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, *args)
            return [dict(row) for row in rows]

    async def fetchone(self, query: str, *args) -> Optional[Dict]:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, *args)
            return dict(row) if row else None
```

#### 2.3.5 Unified Database Interface

**File**: `part1_core_agent/databases/unified_bridge.py`

```python
from typing import List, Dict, Any, Optional
from .chromadb_client import ChromaDBClient
from .mongodb_client import MongoDBClient
from .neo4j_client import Neo4jClient
from .postgres_client import PostgresClient

class UniversalMemoryBridge:
    """Unified interface to all 4 databases"""

    def __init__(self, config: Dict[str, str]):
        self.chroma = ChromaDBClient(config.get('chromadb_url'))
        self.mongo = MongoDBClient(config.get('mongodb_url'))
        self.neo4j = Neo4jClient(
            config.get('neo4j_url'),
            config.get('neo4j_user'),
            config.get('neo4j_password')
        )
        self.postgres = PostgresClient(config.get('postgres_url'))

    async def search(
        self,
        query: str,
        n_results: int = 5,
        category: str = "all"
    ) -> Dict[str, Any]:
        """Search across all databases"""

        # Vector search (semantic)
        vector_results = await self.chroma.search(query, n_results)

        # Document search (metadata)
        doc_filter = {"category": category} if category != "all" else {}
        doc_results = await self.mongo.search_documents(doc_filter, n_results)

        # Knowledge graph (relationships)
        graph_results = await self.neo4j.query_relationships(query, depth=1)

        return {
            "semantic": vector_results,
            "documents": doc_results,
            "relationships": graph_results,
            "total_sources": len(vector_results) + len(doc_results)
        }

    async def ingest(
        self,
        content: str,
        metadata: Dict[str, Any],
        doc_id: str
    ):
        """Ingest document into all databases"""

        # Store in ChromaDB (vector embeddings)
        await self.chroma.add_documents(
            documents=[content],
            metadatas=[metadata],
            ids=[doc_id]
        )

        # Store in MongoDB (full document)
        await self.mongo.store_document({
            "_id": doc_id,
            "content": content,
            "metadata": metadata
        })

        # Store in PostgreSQL (structured data)
        await self.postgres.execute(
            """
            INSERT INTO documents (id, name, category, created_at)
            VALUES ($1, $2, $3, NOW())
            """,
            doc_id, metadata.get('name'), metadata.get('category')
        )
```

---

### 2.4 Input Validation & Sanitization

**File**: `part2_api_layer/validators.py`

```python
from pydantic import BaseModel, Field, validator
import re
import html

class MessageRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=10000)
    requester_id: str = Field(default="user", max_length=100)
    requester_type: str = Field(default="human", pattern="^(human|agent|application)$")

    @validator('message')
    def sanitize_message(cls, v):
        # Remove any potential script injections
        v = html.escape(v)
        # Remove null bytes
        v = v.replace('\x00', '')
        return v.strip()

    @validator('requester_id')
    def validate_requester_id(cls, v):
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('requester_id must be alphanumeric')
        return v
```

---

## Phase 3: Enhanced Functionality

**Goal**: Add features that make the tool more useful and user-friendly

### 3.1 File Upload & Processing

#### 3.1.1 File Upload Endpoint

**File**: `part2_api_layer/api.py` (additions)

```python
from fastapi import UploadFile, File
import aiofiles
import uuid

UPLOAD_DIR = "./uploads"
ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.pptx', '.xlsx', '.txt', '.md', '.html'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

@app.post("/api/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    category: str = "general",
    current_user: User = Depends(get_current_user)
):
    # Validate file extension
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"File type {ext} not allowed")

    # Validate file size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(400, "File too large (max 50MB)")

    # Generate unique filename
    doc_id = str(uuid.uuid4())
    filename = f"{doc_id}{ext}"
    filepath = Path(UPLOAD_DIR) / filename

    # Save file
    async with aiofiles.open(filepath, 'wb') as f:
        await f.write(content)

    # Process with Docling
    try:
        from docling_extractor import DoclingExtractor
        extractor = DoclingExtractor()
        result = extractor.extract(str(filepath))

        # Store in databases
        await agent.tools.load_documentation(
            source=str(filepath),
            name=file.filename,
            category=category,
            target_agent_types=["all"]
        )

        return {
            "doc_id": doc_id,
            "filename": file.filename,
            "size": len(content),
            "chunks": len(result.get('chunks', [])),
            "images": len(result.get('images', [])),
            "status": "processed"
        }
    except Exception as e:
        return {
            "doc_id": doc_id,
            "filename": file.filename,
            "status": "uploaded",
            "processing_error": str(e)
        }
```

#### 3.1.2 Frontend File Upload Component

**File**: `part3_frontend/src/components/FileUpload.jsx`

```jsx
import { useState, useRef } from 'react'
import '../styles/FileUpload.css'

export default function FileUpload({ onUploadComplete }) {
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [error, setError] = useState(null)
  const fileInputRef = useRef(null)

  const handleUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    const formData = new FormData()
    formData.append('file', file)

    setUploading(true)
    setError(null)

    try {
      const response = await fetch('/api/documents/upload', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`)
      }

      const result = await response.json()
      onUploadComplete?.(result)
    } catch (err) {
      setError(err.message)
    } finally {
      setUploading(false)
      setProgress(0)
    }
  }

  return (
    <div className="file-upload">
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleUpload}
        accept=".pdf,.docx,.pptx,.xlsx,.txt,.md"
        hidden
      />
      <button
        onClick={() => fileInputRef.current?.click()}
        disabled={uploading}
        className="upload-button"
      >
        {uploading ? `Uploading... ${progress}%` : '📎 Upload Document'}
      </button>
      {error && <div className="upload-error">{error}</div>}
    </div>
  )
}
```

---

### 3.2 Markdown Rendering in Chat

#### 3.2.1 Install Dependencies

```bash
cd part3_frontend
npm install react-markdown remark-gfm react-syntax-highlighter
```

#### 3.2.2 Create Markdown Component

**File**: `part3_frontend/src/components/MarkdownMessage.jsx`

```jsx
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism'

export default function MarkdownMessage({ content }) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        code({ node, inline, className, children, ...props }) {
          const match = /language-(\w+)/.exec(className || '')
          return !inline && match ? (
            <SyntaxHighlighter
              style={oneDark}
              language={match[1]}
              PreTag="div"
              {...props}
            >
              {String(children).replace(/\n$/, '')}
            </SyntaxHighlighter>
          ) : (
            <code className={className} {...props}>
              {children}
            </code>
          )
        },
        table({ children }) {
          return (
            <div className="table-wrapper">
              <table>{children}</table>
            </div>
          )
        }
      }}
    >
      {content}
    </ReactMarkdown>
  )
}
```

#### 3.2.3 Update AgentChat Component

**File**: `part3_frontend/src/pages/AgentChat.jsx` (update message rendering)

```jsx
import MarkdownMessage from '../components/MarkdownMessage'

// In the render:
{messages.map((msg, i) => (
  <div key={i} className={`message ${msg.role}`}>
    {msg.role === 'assistant' ? (
      <MarkdownMessage content={msg.content} />
    ) : (
      msg.content
    )}
  </div>
))}
```

---

### 3.3 Semantic Skill Detection

Replace keyword matching with embedding-based detection.

**File**: `part1_core_agent/skill_manager.py` (enhanced)

```python
from sentence_transformers import SentenceTransformer
import numpy as np

class SkillManager:
    def __init__(self, skills_base_path: str = "./skills"):
        self.skills_base_path = skills_base_path
        self.skills_cache = {}
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.skill_embeddings = {}

    def load_all_skills(self) -> Dict[str, Dict]:
        skills = self._load_skill_files()

        # Generate embeddings for each skill
        for name, skill in skills.items():
            description = skill['description']
            self.skill_embeddings[name] = self.embedder.encode(description)

        self.skills_cache = skills
        return skills

    def detect_needed_skills(self, message: str, threshold: float = 0.5) -> List[str]:
        """Use semantic similarity to detect needed skills"""

        message_embedding = self.embedder.encode(message)

        scores = {}
        for name, skill_embedding in self.skill_embeddings.items():
            similarity = np.dot(message_embedding, skill_embedding) / (
                np.linalg.norm(message_embedding) * np.linalg.norm(skill_embedding)
            )
            scores[name] = similarity

        # Return skills above threshold, sorted by score
        needed = [
            name for name, score in sorted(scores.items(), key=lambda x: -x[1])
            if score > threshold
        ]

        return needed[:3]  # Max 3 skills
```

---

### 3.4 Conversation Search

#### 3.4.1 Backend Endpoint

**File**: `part2_api_layer/api.py` (addition)

```python
@app.get("/api/agent/chat/{session_id}/search")
async def search_conversation(
    session_id: str,
    q: str,
    current_user: User = Depends(get_current_user)
):
    """Search within a conversation"""

    session_info = session_manager.get_session_info(session_id)
    if not session_info:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = session_info.get("messages", [])
    query_lower = q.lower()

    results = []
    for i, msg in enumerate(messages):
        content = msg.get("content", "").lower()
        if query_lower in content:
            # Find snippet around match
            idx = content.find(query_lower)
            start = max(0, idx - 50)
            end = min(len(content), idx + len(query_lower) + 50)
            snippet = msg["content"][start:end]

            results.append({
                "message_index": i,
                "role": msg.get("role"),
                "snippet": f"...{snippet}...",
                "timestamp": msg.get("timestamp")
            })

    return {
        "query": q,
        "results": results,
        "total_matches": len(results)
    }
```

#### 3.4.2 Frontend Search Component

**File**: `part3_frontend/src/components/ConversationSearch.jsx`

```jsx
import { useState } from 'react'

export default function ConversationSearch({ sessionId, onResultClick }) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [searching, setSearching] = useState(false)

  const handleSearch = async (e) => {
    e.preventDefault()
    if (!query.trim()) return

    setSearching(true)
    try {
      const response = await fetch(
        `/api/agent/chat/${sessionId}/search?q=${encodeURIComponent(query)}`
      )
      const data = await response.json()
      setResults(data.results)
    } finally {
      setSearching(false)
    }
  }

  return (
    <div className="conversation-search">
      <form onSubmit={handleSearch}>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search conversation..."
        />
        <button type="submit" disabled={searching}>
          {searching ? '...' : '🔍'}
        </button>
      </form>

      {results.length > 0 && (
        <div className="search-results">
          {results.map((result, i) => (
            <div
              key={i}
              className="search-result"
              onClick={() => onResultClick(result.message_index)}
            >
              <span className={`role-badge ${result.role}`}>
                {result.role}
              </span>
              <span className="snippet">{result.snippet}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
```

---

### 3.5 Export Conversations

#### 3.5.1 Backend Export Endpoints

**File**: `part2_api_layer/api.py` (additions)

```python
from fastapi.responses import FileResponse
import tempfile

@app.get("/api/agent/chat/{session_id}/export/json")
async def export_json(session_id: str):
    """Export conversation as JSON"""

    session_info = session_manager.get_session_info(session_id)
    if not session_info:
        raise HTTPException(status_code=404, detail="Session not found")

    export_data = {
        "session_id": session_id,
        "exported_at": datetime.utcnow().isoformat(),
        "messages": session_info.get("messages", []),
        "stats": {
            "total_messages": len(session_info.get("messages", [])),
            "created_at": session_info.get("created_at").isoformat()
        }
    }

    return export_data

@app.get("/api/agent/chat/{session_id}/export/markdown")
async def export_markdown(session_id: str):
    """Export conversation as Markdown"""

    session_info = session_manager.get_session_info(session_id)
    if not session_info:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = session_info.get("messages", [])

    md_content = f"# Conversation Export\n\n"
    md_content += f"**Session ID**: {session_id}\n"
    md_content += f"**Exported**: {datetime.utcnow().isoformat()}\n\n"
    md_content += "---\n\n"

    for msg in messages:
        role = msg.get("role", "unknown").capitalize()
        content = msg.get("content", "")
        timestamp = msg.get("timestamp", "")

        md_content += f"### {role}\n"
        md_content += f"*{timestamp}*\n\n"
        md_content += f"{content}\n\n"
        md_content += "---\n\n"

    # Create temp file
    with tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.md',
        delete=False
    ) as f:
        f.write(md_content)
        temp_path = f.name

    return FileResponse(
        temp_path,
        media_type="text/markdown",
        filename=f"conversation_{session_id}.md"
    )
```

---

## Phase 4: Top-Tier Differentiators

**Goal**: Add features that make this tool stand out from competitors

### 4.1 Analytics Dashboard

#### 4.1.1 Analytics Data Models

**File**: `part2_api_layer/analytics.py`

```python
from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime, timedelta
from collections import defaultdict

class UsageMetrics(BaseModel):
    total_sessions: int
    total_messages: int
    total_tokens_used: int
    total_cost: float
    total_savings: float
    avg_response_time: float
    cache_hit_rate: float

class SkillUsageMetrics(BaseModel):
    skill_name: str
    usage_count: int
    avg_response_time: float

class DailyMetrics(BaseModel):
    date: str
    sessions: int
    messages: int
    cost: float

class AnalyticsService:
    def __init__(self):
        self.metrics_store = defaultdict(list)

    def record_interaction(
        self,
        session_id: str,
        tokens: int,
        cost: float,
        savings: float,
        response_time: float,
        cache_hit: bool,
        skills_used: List[str]
    ):
        self.metrics_store['interactions'].append({
            'timestamp': datetime.utcnow(),
            'session_id': session_id,
            'tokens': tokens,
            'cost': cost,
            'savings': savings,
            'response_time': response_time,
            'cache_hit': cache_hit,
            'skills_used': skills_used
        })

    def get_usage_metrics(self, days: int = 30) -> UsageMetrics:
        cutoff = datetime.utcnow() - timedelta(days=days)
        recent = [
            i for i in self.metrics_store['interactions']
            if i['timestamp'] > cutoff
        ]

        if not recent:
            return UsageMetrics(
                total_sessions=0, total_messages=0, total_tokens_used=0,
                total_cost=0, total_savings=0, avg_response_time=0,
                cache_hit_rate=0
            )

        sessions = len(set(i['session_id'] for i in recent))
        cache_hits = sum(1 for i in recent if i['cache_hit'])

        return UsageMetrics(
            total_sessions=sessions,
            total_messages=len(recent),
            total_tokens_used=sum(i['tokens'] for i in recent),
            total_cost=sum(i['cost'] for i in recent),
            total_savings=sum(i['savings'] for i in recent),
            avg_response_time=sum(i['response_time'] for i in recent) / len(recent),
            cache_hit_rate=cache_hits / len(recent) if recent else 0
        )
```

#### 4.1.2 Analytics API Endpoints

```python
analytics_service = AnalyticsService()

@app.get("/api/analytics/usage")
async def get_usage_analytics(
    days: int = 30,
    current_user: User = Depends(get_current_user)
):
    """Get usage analytics"""
    return analytics_service.get_usage_metrics(days)

@app.get("/api/analytics/skills")
async def get_skill_analytics(current_user: User = Depends(get_current_user)):
    """Get skill usage analytics"""
    return analytics_service.get_skill_metrics()

@app.get("/api/analytics/costs")
async def get_cost_analytics(
    days: int = 30,
    current_user: User = Depends(get_current_user)
):
    """Get cost breakdown analytics"""
    return analytics_service.get_cost_breakdown(days)
```

#### 4.1.3 Dashboard Frontend Component

**File**: `part3_frontend/src/pages/Dashboard.jsx`

```jsx
import { useState, useEffect } from 'react'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import '../styles/Dashboard.css'

export default function Dashboard() {
  const [metrics, setMetrics] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchMetrics()
  }, [])

  const fetchMetrics = async () => {
    try {
      const response = await fetch('/api/analytics/usage')
      const data = await response.json()
      setMetrics(data)
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <div>Loading...</div>

  return (
    <div className="dashboard">
      <h1>Analytics Dashboard</h1>

      <div className="metrics-grid">
        <div className="metric-card">
          <h3>Total Sessions</h3>
          <div className="metric-value">{metrics.total_sessions}</div>
        </div>

        <div className="metric-card">
          <h3>Total Messages</h3>
          <div className="metric-value">{metrics.total_messages}</div>
        </div>

        <div className="metric-card">
          <h3>Total Cost</h3>
          <div className="metric-value">${metrics.total_cost.toFixed(2)}</div>
        </div>

        <div className="metric-card savings">
          <h3>Cache Savings</h3>
          <div className="metric-value">${metrics.total_savings.toFixed(2)}</div>
          <div className="metric-subtitle">
            {(metrics.cache_hit_rate * 100).toFixed(1)}% cache hit rate
          </div>
        </div>

        <div className="metric-card">
          <h3>Avg Response Time</h3>
          <div className="metric-value">{metrics.avg_response_time.toFixed(2)}s</div>
        </div>
      </div>

      <div className="chart-section">
        <h2>Usage Over Time</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={metrics.daily_usage}>
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="messages" stroke="#00d4ff" />
            <Line type="monotone" dataKey="cost" stroke="#ff6b6b" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
```

---

### 4.2 Plugin/Extension System

#### 4.2.1 Plugin Interface

**File**: `part1_core_agent/plugins/base.py`

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List

class PluginBase(ABC):
    """Base class for all plugins"""

    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name"""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin version"""
        pass

    @property
    def description(self) -> str:
        """Plugin description"""
        return ""

    @abstractmethod
    def get_tools(self) -> List[Dict]:
        """Return tool definitions for this plugin"""
        pass

    @abstractmethod
    async def execute_tool(self, tool_name: str, tool_input: Dict) -> Any:
        """Execute a tool from this plugin"""
        pass

    def on_load(self):
        """Called when plugin is loaded"""
        pass

    def on_unload(self):
        """Called when plugin is unloaded"""
        pass
```

#### 4.2.2 Plugin Manager

**File**: `part1_core_agent/plugins/manager.py`

```python
import importlib
import os
from pathlib import Path
from typing import Dict, List
from .base import PluginBase

class PluginManager:
    def __init__(self, plugins_dir: str = "./plugins"):
        self.plugins_dir = Path(plugins_dir)
        self.plugins: Dict[str, PluginBase] = {}

    def discover_plugins(self) -> List[str]:
        """Discover available plugins"""
        discovered = []

        if not self.plugins_dir.exists():
            return discovered

        for item in self.plugins_dir.iterdir():
            if item.is_dir() and (item / "__init__.py").exists():
                discovered.append(item.name)

        return discovered

    def load_plugin(self, plugin_name: str) -> bool:
        """Load a plugin by name"""
        try:
            module = importlib.import_module(f"plugins.{plugin_name}")
            plugin_class = getattr(module, "Plugin")
            plugin = plugin_class()

            if not isinstance(plugin, PluginBase):
                raise ValueError(f"{plugin_name} is not a valid plugin")

            plugin.on_load()
            self.plugins[plugin_name] = plugin
            return True
        except Exception as e:
            print(f"Failed to load plugin {plugin_name}: {e}")
            return False

    def unload_plugin(self, plugin_name: str):
        """Unload a plugin"""
        if plugin_name in self.plugins:
            self.plugins[plugin_name].on_unload()
            del self.plugins[plugin_name]

    def get_all_tools(self) -> List[Dict]:
        """Get tools from all loaded plugins"""
        tools = []
        for plugin in self.plugins.values():
            tools.extend(plugin.get_tools())
        return tools

    async def execute_tool(self, tool_name: str, tool_input: Dict) -> Any:
        """Execute a tool from any loaded plugin"""
        for plugin in self.plugins.values():
            tool_names = [t['name'] for t in plugin.get_tools()]
            if tool_name in tool_names:
                return await plugin.execute_tool(tool_name, tool_input)

        raise ValueError(f"Tool {tool_name} not found in any plugin")
```

#### 4.2.3 Example Plugin: GitHub Integration

**File**: `plugins/github/__init__.py`

```python
from plugins.base import PluginBase
from typing import Dict, Any, List
import aiohttp

class Plugin(PluginBase):
    name = "github"
    version = "1.0.0"
    description = "GitHub integration for repository management"

    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN")

    def get_tools(self) -> List[Dict]:
        return [
            {
                "name": "github_search_repos",
                "description": "Search GitHub repositories",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "language": {"type": "string"}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "github_get_issues",
                "description": "Get issues from a repository",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "owner": {"type": "string"},
                        "repo": {"type": "string"},
                        "state": {"type": "string", "enum": ["open", "closed", "all"]}
                    },
                    "required": ["owner", "repo"]
                }
            }
        ]

    async def execute_tool(self, tool_name: str, tool_input: Dict) -> Any:
        if tool_name == "github_search_repos":
            return await self._search_repos(**tool_input)
        elif tool_name == "github_get_issues":
            return await self._get_issues(**tool_input)

    async def _search_repos(self, query: str, language: str = None):
        url = "https://api.github.com/search/repositories"
        q = query
        if language:
            q += f" language:{language}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params={"q": q}) as resp:
                data = await resp.json()
                return {
                    "total": data.get("total_count", 0),
                    "repos": [
                        {"name": r["full_name"], "stars": r["stargazers_count"]}
                        for r in data.get("items", [])[:10]
                    ]
                }
```

---

### 4.3 Knowledge Graph Visualization

#### 4.3.1 Graph Data Endpoint

```python
@app.get("/api/knowledge-graph")
async def get_knowledge_graph(
    center_entity: str = None,
    depth: int = 2,
    current_user: User = Depends(get_current_user)
):
    """Get knowledge graph data for visualization"""

    if agent and hasattr(agent, 'bridge'):
        graph_data = await agent.bridge.neo4j.query_relationships(
            entity=center_entity,
            depth=depth
        )

        # Convert to D3-compatible format
        nodes = []
        links = []
        seen_nodes = set()

        for path in graph_data:
            for node in path.get('nodes', []):
                if node['name'] not in seen_nodes:
                    nodes.append({
                        'id': node['name'],
                        'label': node['name'],
                        'type': node.get('type', 'entity')
                    })
                    seen_nodes.add(node['name'])

            for rel in path.get('relationships', []):
                links.append({
                    'source': rel['source'],
                    'target': rel['target'],
                    'type': rel['type']
                })

        return {"nodes": nodes, "links": links}

    return {"nodes": [], "links": []}
```

#### 4.3.2 Graph Visualization Component

**File**: `part3_frontend/src/components/KnowledgeGraph.jsx`

```jsx
import { useEffect, useRef } from 'react'
import * as d3 from 'd3'

export default function KnowledgeGraph({ data }) {
  const svgRef = useRef()

  useEffect(() => {
    if (!data || !data.nodes.length) return

    const svg = d3.select(svgRef.current)
    const width = 800
    const height = 600

    svg.selectAll("*").remove()

    const simulation = d3.forceSimulation(data.nodes)
      .force("link", d3.forceLink(data.links).id(d => d.id).distance(100))
      .force("charge", d3.forceManyBody().strength(-300))
      .force("center", d3.forceCenter(width / 2, height / 2))

    const link = svg.append("g")
      .selectAll("line")
      .data(data.links)
      .enter().append("line")
      .attr("stroke", "#999")
      .attr("stroke-opacity", 0.6)

    const node = svg.append("g")
      .selectAll("circle")
      .data(data.nodes)
      .enter().append("circle")
      .attr("r", 10)
      .attr("fill", d => d.type === 'skill' ? '#00d4ff' : '#ff6b6b')
      .call(d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended))

    const label = svg.append("g")
      .selectAll("text")
      .data(data.nodes)
      .enter().append("text")
      .text(d => d.label)
      .attr("font-size", 12)
      .attr("dx", 15)
      .attr("dy", 4)

    simulation.on("tick", () => {
      link
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y)

      node
        .attr("cx", d => d.x)
        .attr("cy", d => d.y)

      label
        .attr("x", d => d.x)
        .attr("y", d => d.y)
    })

    function dragstarted(event, d) {
      if (!event.active) simulation.alphaTarget(0.3).restart()
      d.fx = d.x
      d.fy = d.y
    }

    function dragged(event, d) {
      d.fx = event.x
      d.fy = event.y
    }

    function dragended(event, d) {
      if (!event.active) simulation.alphaTarget(0)
      d.fx = null
      d.fy = null
    }
  }, [data])

  return (
    <div className="knowledge-graph">
      <svg ref={svgRef} width={800} height={600}></svg>
    </div>
  )
}
```

---

### 4.4 Observability Stack

#### 4.4.1 Prometheus Metrics

**File**: `part2_api_layer/metrics.py`

```python
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import Response

# Metrics
REQUEST_COUNT = Counter(
    'librarian_requests_total',
    'Total requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'librarian_request_latency_seconds',
    'Request latency',
    ['method', 'endpoint']
)

ACTIVE_SESSIONS = Gauge(
    'librarian_active_sessions',
    'Number of active sessions'
)

TOKEN_USAGE = Counter(
    'librarian_tokens_total',
    'Total tokens used',
    ['type']  # input, output, cache_read, cache_write
)

CACHE_HIT_RATE = Gauge(
    'librarian_cache_hit_rate',
    'Cache hit rate'
)

# Middleware for automatic metrics
from starlette.middleware.base import BaseHTTPMiddleware
import time

class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start_time = time.time()

        response = await call_next(request)

        duration = time.time() - start_time
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()

        REQUEST_LATENCY.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(duration)

        return response

# Metrics endpoint
@app.get("/metrics")
async def metrics():
    return Response(
        generate_latest(),
        media_type="text/plain"
    )
```

#### 4.4.2 OpenTelemetry Tracing

**File**: `part2_api_layer/tracing.py`

```python
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

def setup_tracing(app, service_name: str = "librarian-agent"):
    # Setup tracer provider
    provider = TracerProvider()

    # Configure exporter (Jaeger/Tempo/etc.)
    exporter = OTLPSpanExporter(endpoint="http://localhost:4317")
    provider.add_span_processor(BatchSpanProcessor(exporter))

    trace.set_tracer_provider(provider)

    # Instrument FastAPI
    FastAPIInstrumentor.instrument_app(app)

    return trace.get_tracer(service_name)
```

---

## Implementation Timeline

| Phase | Focus | Key Deliverables |
|-------|-------|------------------|
| **Phase 1** | Foundation | Tests, CI/CD, Config, Logging, Bug fixes |
| **Phase 2** | Security & Data | Auth, Rate limiting, Database integrations |
| **Phase 3** | Features | File upload, Markdown, Search, Export |
| **Phase 4** | Differentiation | Analytics, Plugins, Graph viz, Observability |

---

## Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Test Coverage | 0% | >80% |
| API Response Time (p95) | Unknown | <500ms |
| Cache Hit Rate | Unknown | >70% |
| Uptime | N/A | 99.9% |
| Error Rate | Unknown | <0.1% |
| User Satisfaction | N/A | >4.5/5 |

---

## Next Steps

1. **Immediate**: Fix critical bugs (async issue, missing method)
2. **This Week**: Set up testing infrastructure and CI/CD
3. **Next Sprint**: Implement authentication and database connections
4. **Following Sprint**: Add file upload and markdown rendering

---

*Document created: 2026-01-01*
*Last updated: 2026-01-01*
