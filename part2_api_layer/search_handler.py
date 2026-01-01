from typing import List, Dict, Any

def search_conversation(messages: List[Dict], query: str) -> List[Dict[str, Any]]:
    query_lower = query.lower()
    results = []

    for i, msg in enumerate(messages):
        content = msg.get("content", "")
        content_lower = content.lower()

        if query_lower in content_lower:
            idx = content_lower.find(query_lower)
            start = max(0, idx - 50)
            end = min(len(content), idx + len(query) + 50)
            snippet = content[start:end]

            prefix = "..." if start > 0 else ""
            suffix = "..." if end < len(content) else ""

            results.append({
                "message_index": i,
                "role": msg.get("role"),
                "snippet": f"{prefix}{snippet}{suffix}",
                "timestamp": msg.get("timestamp")
            })

    return results
