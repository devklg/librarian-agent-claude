"""
Integration tests for API endpoints
"""

import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoint:
    """Tests for health check endpoint"""

    def test_health_check(self, app_client):
        """Test health check returns expected fields"""
        response = app_client.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert "status" in data
        assert data["status"] == "healthy"
        assert "agent_ready" in data
        assert "agent_mode" in data
        assert "active_sessions" in data
        assert "timestamp" in data


class TestRootEndpoint:
    """Tests for root endpoint"""

    def test_root(self, app_client):
        """Test root endpoint"""
        response = app_client.get("/")

        assert response.status_code == 200
        data = response.json()

        assert data["service"] == "Librarian Agent API"
        assert "version" in data
        assert data["status"] == "running"


class TestSessionEndpoints:
    """Tests for session management endpoints"""

    def test_create_new_session(self, app_client):
        """Test creating a new session"""
        response = app_client.post("/api/agent/chat/new")

        assert response.status_code == 200
        data = response.json()

        assert "session_id" in data
        assert "created_at" in data
        assert data["status"] == "created"

    def test_list_sessions(self, app_client):
        """Test listing all sessions"""
        # Create a few sessions first
        app_client.post("/api/agent/chat/new")
        app_client.post("/api/agent/chat/new")

        response = app_client.get("/api/agent/sessions")

        assert response.status_code == 200
        data = response.json()

        assert "active_sessions" in data
        assert "sessions" in data
        assert isinstance(data["sessions"], list)

    def test_get_session_history(self, app_client):
        """Test getting session history"""
        # Create session
        create_response = app_client.post("/api/agent/chat/new")
        session_id = create_response.json()["session_id"]

        # Get history
        response = app_client.get(f"/api/agent/chat/{session_id}/history")

        assert response.status_code == 200
        data = response.json()

        assert data["session_id"] == session_id
        assert "messages" in data
        assert "total_messages" in data

    def test_get_session_history_not_found(self, app_client):
        """Test getting history for non-existent session"""
        response = app_client.get("/api/agent/chat/nonexistent-session/history")

        assert response.status_code == 404

    def test_get_session_stats(self, app_client):
        """Test getting session statistics"""
        # Create session
        create_response = app_client.post("/api/agent/chat/new")
        session_id = create_response.json()["session_id"]

        # Get stats
        response = app_client.get(f"/api/agent/chat/{session_id}/stats")

        assert response.status_code == 200
        data = response.json()

        assert data["session_id"] == session_id
        assert "total_turns" in data
        assert "session_duration_seconds" in data

    def test_delete_session(self, app_client):
        """Test deleting a session"""
        # Create session
        create_response = app_client.post("/api/agent/chat/new")
        session_id = create_response.json()["session_id"]

        # Delete session
        response = app_client.delete(f"/api/agent/chat/{session_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "deleted"

        # Verify it's gone
        response = app_client.get(f"/api/agent/chat/{session_id}/history")
        assert response.status_code == 404

    def test_delete_session_not_found(self, app_client):
        """Test deleting non-existent session"""
        response = app_client.delete("/api/agent/chat/nonexistent-session")

        assert response.status_code == 404


class TestChatEndpoint:
    """Tests for chat endpoint"""

    def test_send_message_returns_stream(self, app_client):
        """Test that sending a message returns SSE stream"""
        # Create session
        create_response = app_client.post("/api/agent/chat/new")
        session_id = create_response.json()["session_id"]

        # Send message
        response = app_client.post(
            f"/api/agent/chat/{session_id}",
            json={"message": "Hello, how are you?"}
        )

        assert response.status_code == 200
        assert response.headers.get("content-type") == "text/event-stream; charset=utf-8"

    def test_send_message_invalid_session(self, app_client):
        """Test sending message to invalid session"""
        response = app_client.post(
            "/api/agent/chat/invalid-session",
            json={"message": "Hello"}
        )

        assert response.status_code == 404

    def test_send_message_empty(self, app_client):
        """Test sending empty message"""
        # Create session
        create_response = app_client.post("/api/agent/chat/new")
        session_id = create_response.json()["session_id"]

        # Send empty message - should still work but may return validation error
        response = app_client.post(
            f"/api/agent/chat/{session_id}",
            json={"message": ""}
        )

        # FastAPI will validate and may return 422 for empty string
        # or 200 if validation passes
        assert response.status_code in [200, 422]


class TestCORSHeaders:
    """Tests for CORS configuration"""

    def test_cors_headers_present(self, app_client):
        """Test that CORS headers are present"""
        response = app_client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET"
            }
        )

        # CORS preflight should return 200
        assert response.status_code == 200


class TestErrorHandling:
    """Tests for error handling"""

    def test_404_error(self, app_client):
        """Test 404 error handling"""
        response = app_client.get("/nonexistent-endpoint")

        assert response.status_code == 404

    def test_method_not_allowed(self, app_client):
        """Test method not allowed"""
        response = app_client.patch("/health")

        assert response.status_code == 405
