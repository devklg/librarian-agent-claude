from datetime import datetime
from typing import Dict, Any, List
import json

def export_to_json(session_id: str, messages: List[Dict], stats: Dict) -> Dict[str, Any]:
    return {
        "session_id": session_id,
        "exported_at": datetime.utcnow().isoformat(),
        "messages": messages,
        "stats": stats
    }

def export_to_markdown(session_id: str, messages: List[Dict]) -> str:
    md = f"# Conversation Export\n\n"
    md += f"**Session ID**: {session_id}\n"
    md += f"**Exported**: {datetime.utcnow().isoformat()}\n\n"
    md += "---\n\n"

    for msg in messages:
        role = msg.get("role", "unknown").capitalize()
        content = msg.get("content", "")
        timestamp = msg.get("timestamp", "")

        md += f"### {role}\n"
        if timestamp:
            md += f"*{timestamp}*\n\n"
        md += f"{content}\n\n---\n\n"

    return md

def export_to_html(session_id: str, messages: List[Dict]) -> str:
    html = f"""<!DOCTYPE html>
<html><head><title>Conversation {session_id}</title>
<style>
body {{ font-family: system-ui, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
.message {{ margin: 15px 0; padding: 15px; border-radius: 8px; }}
.user {{ background: #e3f2fd; }}
.assistant {{ background: #f5f5f5; }}
.role {{ font-weight: bold; margin-bottom: 8px; }}
</style></head><body>
<h1>Conversation Export</h1>
<p><strong>Session:</strong> {session_id}</p>
<p><strong>Exported:</strong> {datetime.utcnow().isoformat()}</p>
<hr>
"""
    for msg in messages:
        role = msg.get("role", "unknown")
        content = msg.get("content", "").replace("\n", "<br>")
        html += f'<div class="message {role}"><div class="role">{role.capitalize()}</div>{content}</div>\n'

    html += "</body></html>"
    return html
