from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Any
from pydantic import BaseModel

class UsageMetrics(BaseModel):
    total_sessions: int = 0
    total_messages: int = 0
    total_tokens_used: int = 0
    total_cost: float = 0.0
    total_savings: float = 0.0
    avg_response_time: float = 0.0
    cache_hit_rate: float = 0.0

class AnalyticsService:
    def __init__(self):
        self.interactions: List[Dict] = []
        self.daily_stats: Dict[str, Dict] = defaultdict(lambda: {
            "sessions": set(), "messages": 0, "cost": 0.0, "tokens": 0
        })

    def record_interaction(
        self,
        session_id: str,
        tokens: int = 0,
        cost: float = 0.0,
        savings: float = 0.0,
        response_time: float = 0.0,
        cache_hit: bool = False,
        skills_used: List[str] = None
    ):
        now = datetime.utcnow()
        day_key = now.strftime("%Y-%m-%d")

        self.interactions.append({
            "timestamp": now,
            "session_id": session_id,
            "tokens": tokens,
            "cost": cost,
            "savings": savings,
            "response_time": response_time,
            "cache_hit": cache_hit,
            "skills_used": skills_used or []
        })

        self.daily_stats[day_key]["sessions"].add(session_id)
        self.daily_stats[day_key]["messages"] += 1
        self.daily_stats[day_key]["cost"] += cost
        self.daily_stats[day_key]["tokens"] += tokens

    def get_usage_metrics(self, days: int = 30) -> UsageMetrics:
        cutoff = datetime.utcnow() - timedelta(days=days)
        recent = [i for i in self.interactions if i["timestamp"] > cutoff]

        if not recent:
            return UsageMetrics()

        sessions = set(i["session_id"] for i in recent)
        cache_hits = sum(1 for i in recent if i["cache_hit"])
        total_response_time = sum(i["response_time"] for i in recent)

        return UsageMetrics(
            total_sessions=len(sessions),
            total_messages=len(recent),
            total_tokens_used=sum(i["tokens"] for i in recent),
            total_cost=sum(i["cost"] for i in recent),
            total_savings=sum(i["savings"] for i in recent),
            avg_response_time=total_response_time / len(recent) if recent else 0,
            cache_hit_rate=cache_hits / len(recent) if recent else 0
        )

    def get_daily_usage(self, days: int = 30) -> List[Dict]:
        result = []
        for i in range(days):
            date = (datetime.utcnow() - timedelta(days=i)).strftime("%Y-%m-%d")
            stats = self.daily_stats.get(date, {"sessions": set(), "messages": 0, "cost": 0.0})
            result.append({
                "date": date,
                "sessions": len(stats["sessions"]),
                "messages": stats["messages"],
                "cost": round(stats["cost"], 4)
            })
        return list(reversed(result))

    def get_skill_usage(self) -> List[Dict]:
        skill_counts = defaultdict(int)
        for i in self.interactions:
            for skill in i.get("skills_used", []):
                skill_counts[skill] += 1

        return [{"skill": k, "count": v} for k, v in sorted(skill_counts.items(), key=lambda x: -x[1])]

analytics_service = AnalyticsService()
