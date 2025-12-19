"""
WebSocket Handler - Manage WebSocket connections and streaming
"""

from typing import Dict, Set
from fastapi import WebSocket
import asyncio
import json

class WebSocketHandler:
    """Manages WebSocket connections for real-time communication"""
    
    def __init__(self):
        # Track active connections by session_id
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        """
        Accept and register a new WebSocket connection
        
        Args:
            websocket: WebSocket connection
            session_id: Session ID for this connection
        """
        await websocket.accept()
        
        if session_id not in self.active_connections:
            self.active_connections[session_id] = set()
        
        self.active_connections[session_id].add(websocket)
        print(f"✅ WebSocket connected for session: {session_id}")
    
    def disconnect(self, websocket: WebSocket, session_id: str):
        """
        Remove a WebSocket connection
        
        Args:
            websocket: WebSocket connection to remove
            session_id: Session ID
        """
        if session_id in self.active_connections:
            self.active_connections[session_id].discard(websocket)
            
            # Clean up empty session sets
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
        
        print(f"❌ WebSocket disconnected for session: {session_id}")
    
    async def send_message(self, session_id: str, message: Dict):
        """
        Send a message to all connections for a session
        
        Args:
            session_id: Target session ID
            message: Message dict to send
        """
        if session_id in self.active_connections:
            disconnected = set()
            
            for websocket in self.active_connections[session_id]:
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    print(f"Error sending to WebSocket: {e}")
                    disconnected.add(websocket)
            
            # Clean up disconnected websockets
            for websocket in disconnected:
                self.disconnect(websocket, session_id)
    
    async def broadcast(self, message: Dict):
        """
        Broadcast a message to all active connections
        
        Args:
            message: Message dict to broadcast
        """
        for session_id in list(self.active_connections.keys()):
            await self.send_message(session_id, message)
    
    async def stream_response(self, session_id: str, response_generator):
        """
        Stream response chunks to WebSocket clients
        
        Args:
            session_id: Target session ID
            response_generator: Async generator yielding response chunks
        """
        try:
            async for chunk in response_generator:
                await self.send_message(session_id, {
                    "type": "content",
                    "data": chunk
                })
        except Exception as e:
            await self.send_message(session_id, {
                "type": "error",
                "message": str(e)
            })
    
    def get_connection_count(self, session_id: str = None) -> int:
        """
        Get number of active connections
        
        Args:
            session_id: Optional session ID to get count for specific session
            
        Returns:
            Number of active connections
        """
        if session_id:
            return len(self.active_connections.get(session_id, set()))
        
        return sum(len(conns) for conns in self.active_connections.values())
    
    def get_active_sessions(self) -> list:
        """Get list of session IDs with active connections"""
        return list(self.active_connections.keys())
