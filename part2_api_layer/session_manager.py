"""
Session Manager - Track conversation sessions and state
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional

class SessionManager:
    """Manages conversation sessions and their state"""
    
    def __init__(self):
        self.sessions: Dict[str, Dict] = {}
    
    def create_session(self) -> str:
        """
        Create a new session
        
        Returns:
            str: New session ID
        """
        session_id = str(uuid.uuid4())
        
        self.sessions[session_id] = {
            "session_id": session_id,
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow(),
            "turn_count": 0,
            "messages": [],
            "metadata": {}
        }
        
        print(f"✅ Session created: {session_id}")
        return session_id
    
    def get_session_info(self, session_id: str) -> Optional[Dict]:
        """
        Get session information
        
        Args:
            session_id: Session ID to retrieve
            
        Returns:
            Session info dict or None if not found
        """
        return self.sessions.get(session_id)
    
    def update_activity(self, session_id: str):
        """
        Update last activity time and increment turn count
        
        Args:
            session_id: Session ID to update
        """
        if session_id in self.sessions:
            self.sessions[session_id]["last_activity"] = datetime.utcnow()
            self.sessions[session_id]["turn_count"] += 1
    
    def add_message(self, session_id: str, message: Dict):
        """
        Add a message to the session history
        
        Args:
            session_id: Session ID
            message: Message dict with role, content, timestamp
        """
        if session_id in self.sessions:
            self.sessions[session_id]["messages"].append(message)
            self.update_activity(session_id)
    
    def list_active_sessions(self) -> List[Dict]:
        """
        List all active sessions
        
        Returns:
            List of session info dicts
        """
        return list(self.sessions.values())
    
    def cleanup_old_sessions(self, max_age_minutes: int = 60):
        """
        Remove sessions older than max_age_minutes
        
        Args:
            max_age_minutes: Maximum age in minutes before cleanup
        """
        current_time = datetime.utcnow()
        sessions_to_remove = []
        
        for session_id, session_info in self.sessions.items():
            last_activity = session_info.get("last_activity")
            if last_activity:
                age_minutes = (current_time - last_activity).total_seconds() / 60
                if age_minutes > max_age_minutes:
                    sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            del self.sessions[session_id]
            print(f"🗑️  Cleaned up old session: {session_id}")
        
        if sessions_to_remove:
            print(f"✅ Cleaned up {len(sessions_to_remove)} old sessions")
    
    def get_session_count(self) -> int:
        """Get total number of active sessions"""
        return len(self.sessions)
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a specific session
        
        Args:
            session_id: Session ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            print(f"🗑️  Session deleted: {session_id}")
            return True
        return False
