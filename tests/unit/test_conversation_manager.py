"""
Unit tests for ConversationManager
"""

import pytest
import time
from conversation_manager import ConversationManager


class TestConversationManager:
    """Tests for ConversationManager class"""

    def test_init(self):
        """Test initialization"""
        manager = ConversationManager()
        assert manager.cache_ttl == 300  # Default 5 minutes
        assert len(manager.conversations) == 0

    def test_init_custom_ttl(self):
        """Test initialization with custom TTL"""
        manager = ConversationManager(cache_ttl=600)
        assert manager.cache_ttl == 600

    def test_add_turn(self, sample_session_id):
        """Test adding a conversation turn"""
        manager = ConversationManager()

        manager.add_turn(
            session_id=sample_session_id,
            user_message="Hello",
            agent_response="Hi there!",
            tool_calls=[],
            skills_used=[]
        )

        conversation = manager.get_conversation(sample_session_id)
        assert len(conversation) == 1
        assert conversation[0]["user_message"] == "Hello"
        assert conversation[0]["agent_response"] == "Hi there!"

    def test_add_multiple_turns(self, sample_session_id):
        """Test adding multiple conversation turns"""
        manager = ConversationManager()

        manager.add_turn(sample_session_id, "Hello", "Hi!", [], [])
        manager.add_turn(sample_session_id, "How are you?", "I'm good!", [], [])
        manager.add_turn(sample_session_id, "Great!", "Glad to hear!", [], [])

        conversation = manager.get_conversation(sample_session_id)
        assert len(conversation) == 3

    def test_get_conversation_empty(self):
        """Test getting conversation for non-existent session"""
        manager = ConversationManager()
        conversation = manager.get_conversation("nonexistent")
        assert conversation == []

    def test_get_last_n_turns(self, sample_session_id):
        """Test getting last N turns"""
        manager = ConversationManager()

        # Add 5 turns
        for i in range(5):
            manager.add_turn(
                sample_session_id,
                f"Message {i}",
                f"Response {i}",
                [],
                []
            )

        # Get last 3
        last_3 = manager.get_last_n_turns(sample_session_id, 3)
        assert len(last_3) == 3
        assert last_3[0]["user_message"] == "Message 2"
        assert last_3[2]["user_message"] == "Message 4"

    def test_get_last_n_turns_less_than_n(self, sample_session_id):
        """Test getting last N turns when less than N exist"""
        manager = ConversationManager()

        manager.add_turn(sample_session_id, "Hello", "Hi!", [], [])

        last_5 = manager.get_last_n_turns(sample_session_id, 5)
        assert len(last_5) == 1

    def test_session_cache_set_get(self, sample_session_id):
        """Test session cache set and get"""
        manager = ConversationManager()

        manager.set_session_cache(sample_session_id, "docs", "cached docs content")
        cached = manager.get_session_cache(sample_session_id, "docs")

        assert cached == "cached docs content"

    def test_session_cache_not_found(self, sample_session_id):
        """Test getting non-existent cache key"""
        manager = ConversationManager()
        cached = manager.get_session_cache(sample_session_id, "nonexistent")
        assert cached is None

    def test_session_cache_expiry(self, sample_session_id):
        """Test session cache expiration"""
        manager = ConversationManager(cache_ttl=1)  # 1 second TTL

        manager.set_session_cache(sample_session_id, "docs", "content")

        # Should exist immediately
        assert manager.get_session_cache(sample_session_id, "docs") == "content"

        # Wait for expiry
        time.sleep(1.5)

        # Should be expired
        assert manager.get_session_cache(sample_session_id, "docs") is None

    def test_clear_session_cache(self, sample_session_id):
        """Test clearing session cache"""
        manager = ConversationManager()

        manager.set_session_cache(sample_session_id, "docs", "content")
        manager.set_session_cache(sample_session_id, "skills", "skills content")

        manager.clear_session_cache(sample_session_id)

        assert manager.get_session_cache(sample_session_id, "docs") is None
        assert manager.get_session_cache(sample_session_id, "skills") is None

    def test_get_session_stats(self, sample_session_id, sample_conversation):
        """Test getting session statistics"""
        manager = ConversationManager()

        # Add turns with tool calls and skills
        manager.add_turn(
            sample_session_id,
            "Create a document",
            "I'll create that for you",
            [{"name": "create_doc", "id": "123"}],
            ["docx"]
        )
        manager.add_turn(
            sample_session_id,
            "Add a table",
            "Table added",
            [{"name": "add_table", "id": "124"}],
            ["docx"]
        )

        stats = manager.get_session_stats(sample_session_id)

        assert stats["session_id"] == sample_session_id
        assert stats["total_turns"] == 2
        assert stats["total_tools_used"] == 2
        assert "docx" in stats["unique_skills_used"]

    def test_get_session_stats_empty(self):
        """Test getting stats for non-existent session"""
        manager = ConversationManager()
        stats = manager.get_session_stats("nonexistent")
        assert stats["turns"] == 0

    def test_get_active_session_count(self):
        """Test counting active sessions"""
        manager = ConversationManager()

        assert manager.get_active_session_count() == 0

        manager.add_turn("session1", "Hi", "Hello", [], [])
        manager.add_turn("session2", "Hey", "Hi there", [], [])
        manager.add_turn("session3", "Hello", "Greetings", [], [])

        assert manager.get_active_session_count() == 3

    def test_get_all_sessions(self):
        """Test getting all session IDs"""
        manager = ConversationManager()

        manager.add_turn("session1", "Hi", "Hello", [], [])
        manager.add_turn("session2", "Hey", "Hi there", [], [])

        sessions = manager.get_all_sessions()
        assert "session1" in sessions
        assert "session2" in sessions
        assert len(sessions) == 2

    def test_cleanup_old_sessions(self):
        """Test cleaning up old sessions"""
        manager = ConversationManager()

        # Add a session
        manager.add_turn("old_session", "Hi", "Hello", [], [])

        # Manually set old timestamp
        manager.conversations["old_session"][0]["timestamp"] = time.time() - 7200

        # Cleanup sessions older than 1 hour
        removed = manager.cleanup_old_sessions(max_age=3600)

        assert removed == 1
        assert "old_session" not in manager.conversations

    def test_export_conversation(self, sample_session_id):
        """Test exporting conversation"""
        manager = ConversationManager()

        manager.add_turn(sample_session_id, "Hello", "Hi!", [], [])
        manager.add_turn(sample_session_id, "Bye", "Goodbye!", [], [])

        export = manager.export_conversation(sample_session_id)

        assert export["session_id"] == sample_session_id
        assert "stats" in export
        assert "conversation" in export
        assert len(export["conversation"]) == 2
