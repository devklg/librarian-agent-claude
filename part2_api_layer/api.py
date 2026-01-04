"""
Librarian Agent API - FastAPI REST API with SSE streaming and WebSocket support
"""

from fastapi import FastAPI, WebSocket, HTTPException, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
import sys
import json
import asyncio
from datetime import datetime
import os

# Import Part 1
sys.path.append('../part1_core_agent')
try:
    from librarian_claude_agent import LibrarianClaudeAgent
except ImportError:
    print("Warning: Could not import LibrarianClaudeAgent. Using mock mode.")
    LibrarianClaudeAgent = None

# Import components
from session_manager import SessionManager
from websocket_handler import WebSocketHandler

# Pydantic Models
class MessageRequest(BaseModel):
    message: str
    requester_id: str = "user"
    requester_type: str = "human"

class MessageResponse(BaseModel):
    session_id: str
    message: str
    tool_calls: List[Dict] = []
    skills_used: List[str] = []
    cost: Dict = {}
    usage: Dict = {}
    response_time: float
    cache_hit: bool = False

class SessionStats(BaseModel):
    session_id: str
    total_turns: int
    total_tools_used: int
    unique_skills_used: List[str]
    session_duration_seconds: float
    total_cost: float
    total_savings: float
    cache_hit_rate: float

# Initialize FastAPI
app = FastAPI(
    title="Librarian Agent API",
    version="1.0.0",
    description="Intelligent knowledge keeper powered by Claude SDK"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
agent = None
session_manager = SessionManager()
ws_handler = WebSocketHandler()

@app.on_event("startup")
async def startup():
    """Initialize on startup"""
    global agent
    
    print("🚀 Starting Librarian Agent API...")
    
    # Check for API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("⚠️  Warning: ANTHROPIC_API_KEY not set. Using mock mode.")
        agent = None
    else:
        # Initialize agent
        if LibrarianClaudeAgent:
            try:
                agent = LibrarianClaudeAgent()
                print("✅ Librarian Agent initialized successfully")
            except Exception as e:
                print(f"❌ Failed to initialize agent: {e}")
                agent = None
        else:
            print("⚠️  Running in mock mode - LibrarianClaudeAgent not available")
            agent = None
    
    print("✅ Librarian Agent API ready on http://localhost:9600")

@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    print("👋 Shutting down Librarian Agent API...")

# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Librarian Agent API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """
    Check API and agent health
    """
    agent_ready = agent is not None
    
    return {
        "status": "healthy",
        "agent_ready": agent_ready,
        "agent_mode": "production" if agent_ready else "mock",
        "api_key_configured": os.getenv("ANTHROPIC_API_KEY") is not None,
        "active_sessions": len(session_manager.sessions),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/agent/chat/new")
async def new_conversation():
    """
    Create a new conversation session
    """
    session_id = session_manager.create_session()
    
    # Initialize agent conversation if agent is available
    if agent:
        try:
            agent.start_conversation(session_id)
        except Exception as e:
            print(f"Warning: Could not start agent conversation: {e}")
    
    return {
        "session_id": session_id,
        "created_at": datetime.utcnow().isoformat(),
        "status": "created"
    }

async def generate_sse_stream(session_id: str, message: str, agent_instance):
    """Generate Server-Sent Events stream for agent responses"""
    
    # Start event
    yield f"event: message_start\n"
    yield f"data: {json.dumps({'session_id': session_id, 'timestamp': datetime.utcnow().isoformat()})}\n\n"
    
    try:
        if agent_instance:
            # Use real agent
            response = await agent_instance.chat(
                message=message,
                session_id=session_id
            )
            
            # Stream the response content
            full_message = response.get('message', '')
            words = full_message.split()
            
            for word in words:
                yield f"event: content\n"
                yield f"data: {json.dumps({'text': word + ' '})}\n\n"
                await asyncio.sleep(0.03)  # Smooth streaming effect
            
            # Tool calls
            for tool_call in response.get('tool_calls', []):
                yield f"event: tool_call\n"
                yield f"data: {json.dumps(tool_call)}\n\n"
            
            # End event with metadata
            yield f"event: message_end\n"
            yield f"data: {json.dumps({
                'cost': response.get('cost', {}),
                'usage': response.get('usage', {}),
                'cache_hit': response.get('cache_hit', False),
                'skills_used': response.get('skills_used', [])
            })}\n\n"
            
        else:
            # Mock mode - simulate response
            mock_response = (
                "I'm currently running in mock mode as the Claude API key is not configured. "
                f"To enable full functionality, please set the ANTHROPIC_API_KEY environment variable. "
                f"Your message was: '{message}'"
            )
            
            words = mock_response.split()
            for word in words:
                yield f"event: content\n"
                yield f"data: {json.dumps({'text': word + ' '})}\n\n"
                await asyncio.sleep(0.03)
            
            yield f"event: message_end\n"
            yield f"data: {json.dumps({'mode': 'mock', 'cost': {'total': 0}})}\n\n"
            
    except Exception as e:
        # Error event
        yield f"event: error\n"
        yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    # Update session activity
    session_manager.update_activity(session_id)

@app.post("/api/agent/chat/{session_id}")
async def send_message(session_id: str, request: MessageRequest):
    """
    Send message and get streaming response using Server-Sent Events
    """
    # Validate session
    session_info = session_manager.get_session_info(session_id)
    if not session_info:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Store user message
    session_manager.add_message(session_id, {
        "role": "user",
        "content": request.message,
        "timestamp": datetime.utcnow().isoformat()
    })
    
    # Return SSE stream
    return StreamingResponse(
        generate_sse_stream(session_id, request.message, agent),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@app.get("/api/agent/chat/{session_id}/history")
async def get_history(session_id: str):
    """
    Get full conversation history
    """
    session_info = session_manager.get_session_info(session_id)
    if not session_info:
        raise HTTPException(status_code=404, detail="Session not found")
    
    messages = session_info.get("messages", [])
    
    return {
        "session_id": session_id,
        "messages": messages,
        "total_messages": len(messages),
        "created_at": session_info.get("created_at"),
        "last_activity": session_info.get("last_activity")
    }

@app.get("/api/agent/chat/{session_id}/stats")
async def get_stats(session_id: str):
    """
    Get session statistics
    """
    session_info = session_manager.get_session_info(session_id)
    if not session_info:
        raise HTTPException(status_code=404, detail="Session not found")
    
    created_at = session_info.get("created_at")
    last_activity = session_info.get("last_activity")
    
    duration = 0
    if created_at and last_activity:
        duration = (last_activity - created_at).total_seconds()
    
    return {
        "session_id": session_id,
        "total_turns": session_info.get("turn_count", 0),
        "total_messages": len(session_info.get("messages", [])),
        "session_duration_seconds": duration,
        "created_at": created_at.isoformat() if created_at else None,
        "last_activity": last_activity.isoformat() if last_activity else None
    }

@app.get("/api/agent/sessions")
async def list_sessions():
    """
    List all active sessions
    """
    sessions = session_manager.list_active_sessions()
    
    return {
        "active_sessions": len(sessions),
        "sessions": [
            {
                "session_id": s["session_id"],
                "created_at": s["created_at"].isoformat() if s.get("created_at") else None,
                "last_activity": s["last_activity"].isoformat() if s.get("last_activity") else None,
                "turn_count": s.get("turn_count", 0),
                "message_count": len(s.get("messages", []))
            }
            for s in sessions
        ]
    }

@app.websocket("/ws/agent/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket for real-time bi-directional communication
    """
    await websocket.accept()
    
    try:
        # Validate session
        session_info = session_manager.get_session_info(session_id)
        if not session_info:
            await websocket.send_json({
                "type": "error",
                "message": "Session not found"
            })
            await websocket.close()
            return
        
        # Send welcome message
        await websocket.send_json({
            "type": "connected",
            "session_id": session_id,
            "message": "WebSocket connected successfully"
        })
        
        # Listen for messages
        while True:
            data = await websocket.receive_json()
            
            if data.get("type") == "message":
                message = data.get("content", "")
                
                # Send start event
                await websocket.send_json({
                    "type": "start",
                    "session_id": session_id
                })
                
                # Process with agent
                if agent:
                    try:
                        response = await agent.chat(
                            message=message,
                            session_id=session_id
                        )
                        
                        # Send response chunks
                        full_message = response.get('message', '')
                        words = full_message.split()
                        
                        for word in words:
                            await websocket.send_json({
                                "type": "content",
                                "text": word + " "
                            })
                            await asyncio.sleep(0.03)
                        
                        # Send completion
                        await websocket.send_json({
                            "type": "end",
                            "cost": response.get('cost', {}),
                            "usage": response.get('usage', {})
                        })
                        
                    except Exception as e:
                        await websocket.send_json({
                            "type": "error",
                            "message": str(e)
                        })
                else:
                    # Mock response
                    await websocket.send_json({
                        "type": "content",
                        "text": f"Mock response: Received your message '{message}'. API key not configured."
                    })
                    await websocket.send_json({
                        "type": "end",
                        "mode": "mock"
                    })
                
                # Update session
                session_manager.update_activity(session_id)
                
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        print(f"WebSocket error: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": str(e)
            })
        except:
            pass

@app.delete("/api/agent/chat/{session_id}")
async def delete_session(session_id: str):
    """Delete a session"""
    if session_id in session_manager.sessions:
        del session_manager.sessions[session_id]
        return {"status": "deleted", "session_id": session_id}
    raise HTTPException(status_code=404, detail="Session not found")

# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return {
        "error": exc.detail,
        "status_code": exc.status_code
    }

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("API_PORT", "9600"))
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
