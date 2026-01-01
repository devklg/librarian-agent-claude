"""
API Extensions - Additional endpoints for Phases 2, 3, and 4
Import these into main api.py
"""

from fastapi import APIRouter, UploadFile, File, Depends, Query
from fastapi.responses import PlainTextResponse, HTMLResponse
from typing import Optional
from datetime import datetime

router = APIRouter()

# Import handlers (will be created by other agents)
try:
    from file_upload import handle_file_upload
    from export_handler import export_to_json, export_to_markdown, export_to_html
    from search_handler import search_conversation
    from analytics import analytics_service
    from metrics import metrics
    from auth import get_current_user_optional, User
    from rate_limit import rate_limit_middleware
    from validators import MessageRequest, DocumentUploadRequest
except ImportError as e:
    print(f"Warning: Some modules not yet available: {e}")


# ============================================================================
# File Upload Endpoints
# ============================================================================

@router.post("/api/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    category: str = "general"
):
    """Upload a document for processing"""
    try:
        result = await handle_file_upload(file, category)
        return result
    except Exception as e:
        return {"error": str(e), "status": "failed"}


# ============================================================================
# Export Endpoints
# ============================================================================

@router.get("/api/agent/chat/{session_id}/export/json")
async def export_json_endpoint(session_id: str):
    """Export conversation as JSON"""
    # Import session_manager from main api
    from api import session_manager

    session_info = session_manager.get_session_info(session_id)
    if not session_info:
        return {"error": "Session not found"}

    messages = session_info.get("messages", [])
    stats = {"total_messages": len(messages)}
    return export_to_json(session_id, messages, stats)


@router.get("/api/agent/chat/{session_id}/export/markdown")
async def export_markdown_endpoint(session_id: str):
    """Export conversation as Markdown"""
    from api import session_manager

    session_info = session_manager.get_session_info(session_id)
    if not session_info:
        return PlainTextResponse("Session not found", status_code=404)

    messages = session_info.get("messages", [])
    md_content = export_to_markdown(session_id, messages)
    return PlainTextResponse(md_content, media_type="text/markdown")


@router.get("/api/agent/chat/{session_id}/export/html")
async def export_html_endpoint(session_id: str):
    """Export conversation as HTML"""
    from api import session_manager

    session_info = session_manager.get_session_info(session_id)
    if not session_info:
        return HTMLResponse("Session not found", status_code=404)

    messages = session_info.get("messages", [])
    html_content = export_to_html(session_id, messages)
    return HTMLResponse(html_content)


# ============================================================================
# Search Endpoints
# ============================================================================

@router.get("/api/agent/chat/{session_id}/search")
async def search_in_conversation(
    session_id: str,
    q: str = Query(..., min_length=1)
):
    """Search within a conversation"""
    from api import session_manager

    session_info = session_manager.get_session_info(session_id)
    if not session_info:
        return {"error": "Session not found", "results": []}

    messages = session_info.get("messages", [])
    results = search_conversation(messages, q)

    return {
        "query": q,
        "session_id": session_id,
        "results": results,
        "total_matches": len(results)
    }


# ============================================================================
# Analytics Endpoints
# ============================================================================

@router.get("/api/analytics/usage")
async def get_usage_analytics(days: int = 30):
    """Get usage analytics"""
    try:
        return analytics_service.get_usage_metrics(days)
    except:
        return {"total_sessions": 0, "total_messages": 0, "total_cost": 0}


@router.get("/api/analytics/daily")
async def get_daily_analytics(days: int = 30):
    """Get daily usage statistics"""
    try:
        return analytics_service.get_daily_usage(days)
    except:
        return []


@router.get("/api/analytics/skills")
async def get_skill_analytics():
    """Get skill usage analytics"""
    try:
        return analytics_service.get_skill_usage()
    except:
        return []


# ============================================================================
# Metrics Endpoint
# ============================================================================

@router.get("/metrics")
async def get_metrics():
    """Get Prometheus-style metrics"""
    try:
        return PlainTextResponse(metrics.get_metrics_text(), media_type="text/plain")
    except:
        return PlainTextResponse("# No metrics available\n", media_type="text/plain")


# ============================================================================
# Knowledge Graph Endpoint
# ============================================================================

@router.get("/api/knowledge-graph")
async def get_knowledge_graph(
    center_entity: Optional[str] = None,
    depth: int = 2
):
    """Get knowledge graph data for visualization"""
    # Return sample data structure for now
    return {
        "nodes": [
            {"id": "docx", "label": "DOCX Skill", "type": "skill"},
            {"id": "pdf", "label": "PDF Skill", "type": "skill"},
            {"id": "xlsx", "label": "XLSX Skill", "type": "skill"},
            {"id": "documents", "label": "Documents", "type": "category"},
        ],
        "links": [
            {"source": "docx", "target": "documents", "type": "belongs_to"},
            {"id": "pdf", "target": "documents", "type": "belongs_to"},
            {"source": "xlsx", "target": "documents", "type": "belongs_to"},
        ]
    }


# ============================================================================
# Plugin Endpoints
# ============================================================================

@router.get("/api/plugins")
async def list_plugins():
    """List available plugins"""
    try:
        from plugins import PluginManager
        manager = PluginManager()
        return {"plugins": manager.list_plugins()}
    except:
        return {"plugins": []}


def get_router():
    """Return the router for inclusion in main app"""
    return router
