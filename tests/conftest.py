"""
Pytest configuration and shared fixtures for Librarian Agent tests
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch

# Add project paths to sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "part1_core_agent"))
sys.path.insert(0, str(project_root / "part2_api_layer"))


@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic client for testing without API calls"""
    mock_client = Mock()

    # Mock messages.create response
    mock_response = Mock()
    mock_response.content = [Mock(type="text", text="Mock response")]
    mock_response.stop_reason = "end_turn"
    mock_response.usage = Mock(
        input_tokens=100,
        output_tokens=50,
        cache_creation_input_tokens=0,
        cache_read_input_tokens=0
    )

    mock_client.messages.create = AsyncMock(return_value=mock_response)

    return mock_client


@pytest.fixture
def sample_session_id():
    """Generate a sample session ID"""
    return "test-session-12345"


@pytest.fixture
def sample_message():
    """Sample user message for testing"""
    return "How do I create a Word document?"


@pytest.fixture
def sample_conversation():
    """Sample conversation history"""
    return [
        {
            "timestamp": 1704067200,
            "user_message": "Hello",
            "agent_response": "Hi! How can I help you?",
            "tool_calls": [],
            "skills_used": []
        },
        {
            "timestamp": 1704067260,
            "user_message": "I need help with Excel",
            "agent_response": "I can help with Excel! What do you need?",
            "tool_calls": [],
            "skills_used": ["xlsx"]
        }
    ]


@pytest.fixture
def mock_skill_content():
    """Sample skill content for testing"""
    return {
        "docx": {
            "content": "# DOCX Skill\n\nGuide for creating Word documents.",
            "description": "Expert guide for Word documents",
            "path": "/skills/public/docx/SKILL.md",
            "category": "public"
        },
        "xlsx": {
            "content": "# XLSX Skill\n\nGuide for creating Excel spreadsheets.",
            "description": "Expert guide for Excel spreadsheets",
            "path": "/skills/public/xlsx/SKILL.md",
            "category": "public"
        }
    }


@pytest.fixture
def mock_search_results():
    """Sample search results for testing"""
    return {
        "success": True,
        "query": "test query",
        "results": [
            "Result 1: Relevant documentation",
            "Result 2: More documentation"
        ],
        "sources": [
            {"module": "Test Module 1", "priority": "HIGH"},
            {"module": "Test Module 2", "priority": "MEDIUM"}
        ],
        "tokens_saved": 5000
    }


@pytest.fixture
def app_client():
    """FastAPI test client"""
    from fastapi.testclient import TestClient
    from api import app

    return TestClient(app)


@pytest.fixture
async def async_app_client():
    """Async FastAPI test client for async tests"""
    from httpx import AsyncClient, ASGITransport
    from api import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def temp_skills_dir(tmp_path):
    """Create temporary skills directory for testing"""
    skills_dir = tmp_path / "skills" / "public" / "docx"
    skills_dir.mkdir(parents=True)

    skill_file = skills_dir / "SKILL.md"
    skill_file.write_text("# Test DOCX Skill\n\nThis is a test skill.")

    return tmp_path / "skills"


@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset any singletons between tests"""
    yield
    # Cleanup after test if needed


# Pytest markers
def pytest_configure(config):
    """Configure custom pytest markers"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
