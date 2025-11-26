"""
Conversation Manager - Manages conversation state and session caching
"""

import time
from typing import Dict, List, Optional, Any
from collections import defaultdict


class ConversationManager:
    """
    Manages:
    - Conversation history per session
    - Session-level caching (documentation, context)
    - Conversation statistics
    """
    
    def __init__(self, cache_ttl: int = 300):  # 5 minutes cache TTL
        self.conversations = defaultdict(list)  # session_id -> list of turns
        self.session_cache = defaultdict(dict)  # session_id -> {key: value}
        self.cache_timestamps = defaultdict(dict)  # session_id -> {key: timestamp}
        self.cache_ttl = cache_ttl
        self.session_start_times = {}
    
    def add_turn(
        self,
        session_id: str,
        user_message: str,
        agent_response: str,
        tool_calls: List[Dict] = None,
        skills_used: List[str] = None
    ):
        """Add a conversation turn"""
        
        if session_id not in self.session_start_times:
            self.session_start_times[session_id] = time.time()
        
        turn = {
            "timestamp": time.time(),
            "user_message": user_message,
            "agent_response": agent_response,
            "tool_calls": tool_calls or [],
            "skills_used": skills_used or []
        }
        
        self.conversations[session_id].append(turn)
    
    def get_conversation(self, session_id: str) -> List[Dict]:
        """Get full conversation history for a session"""
        
        return self.conversations.get(session_id, [])
    
    def get_last_n_turns(self, session_id: str, n: int = 5) -> List[Dict]:
        """Get last N conversation turns"""
        
        conversation = self.get_conversation(session_id)
        return conversation[-n:] if len(conversation) > n else conversation
    
    def set_session_cache(self, session_id: str, key: str, value: Any):
        """Cache data at session level (e.g., loaded documentation)"""
        
        self.session_cache[session_id][key] = value
        self.cache_timestamps[session_id][key] = time.time()
    
    def get_session_cache(self, session_id: str, key: str) -> Optional[Any]:
        """Get cached data for a session"""
        
        # Check if cache exists
        if key not in self.session_cache.get(session_id, {}):
            return None
        
        # Check if cache is expired
        cache_age = time.time() - self.cache_timestamps[session_id][key]
        if cache_age > self.cache_ttl:
            # Cache expired
            del self.session_cache[session_id][key]
            del self.cache_timestamps[session_id][key]
            return None
        
        return self.session_cache[session_id][key]
    
    def clear_session_cache(self, session_id: str):
        """Clear all cache for a session"""
        
        if session_id in self.session_cache:
            del self.session_cache[session_id]
        if session_id in self.cache_timestamps:
            del self.cache_timestamps[session_id]
    
    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """Get statistics for a session"""
        
        conversation = self.get_conversation(session_id)
        
        if not conversation:
            return {"session_id": session_id, "turns": 0}
        
        # Calculate stats
        total_turns = len(conversation)
        tools_used = sum(len(turn.get('tool_calls', [])) for turn in conversation)
        skills_used = set()
        for turn in conversation:
            skills_used.update(turn.get('skills_used', []))
        
        # Session duration
        start_time = self.session_start_times.get(session_id, time.time())
        duration = time.time() - start_time
        
        return {
            "session_id": session_id,
            "total_turns": total_turns,
            "total_tools_used": tools_used,
            "unique_skills_used": list(skills_used),
            "session_duration_seconds": duration,
            "cache_keys": list(self.session_cache.get(session_id, {}).keys()),
            "first_message_time": conversation[0]['timestamp'],
            "last_message_time": conversation[-1]['timestamp']
        }
    
    def get_active_session_count(self) -> int:
        """Get number of active sessions"""
        
        return len(self.conversations)
    
    def get_all_sessions(self) -> List[str]:
        """Get list of all session IDs"""
        
        return list(self.conversations.keys())
    
    def cleanup_old_sessions(self, max_age: int = 3600):
        """Clean up sessions older than max_age seconds"""
        
        current_time = time.time()
        sessions_to_remove = []
        
        for session_id, conversation in self.conversations.items():
            if not conversation:
                continue
            
            last_message_time = conversation[-1]['timestamp']
            age = current_time - last_message_time
            
            if age > max_age:
                sessions_to_remove.append(session_id)
        
        # Remove old sessions
        for session_id in sessions_to_remove:
            del self.conversations[session_id]
            self.clear_session_cache(session_id)
            if session_id in self.session_start_times:
                del self.session_start_times[session_id]
        
        return len(sessions_to_remove)
    
    def export_conversation(self, session_id: str) -> Dict[str, Any]:
        """Export full conversation history"""
        
        conversation = self.get_conversation(session_id)
        stats = self.get_session_stats(session_id)
        
        return {
            "session_id": session_id,
            "stats": stats,
            "conversation": conversation
        }
