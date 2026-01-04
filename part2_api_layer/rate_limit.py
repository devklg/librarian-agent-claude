from collections import defaultdict
from datetime import datetime, timedelta
from fastapi import Request, HTTPException
from typing import Dict, Tuple
import asyncio

class RateLimiter:
    def __init__(self):
        self.requests: Dict[str, list] = defaultdict(list)
        self.lock = asyncio.Lock()

    async def check_rate_limit(
        self,
        key: str,
        max_requests: int = 60,
        window_seconds: int = 60
    ) -> Tuple[bool, int]:
        async with self.lock:
            now = datetime.utcnow()
            window_start = now - timedelta(seconds=window_seconds)

            self.requests[key] = [
                req_time for req_time in self.requests[key]
                if req_time > window_start
            ]

            if len(self.requests[key]) >= max_requests:
                return False, max_requests - len(self.requests[key])

            self.requests[key].append(now)
            return True, max_requests - len(self.requests[key])

rate_limiter = RateLimiter()

async def rate_limit_middleware(request: Request, max_requests: int = 60):
    client_ip = request.client.host if request.client else "unknown"
    allowed, remaining = await rate_limiter.check_rate_limit(client_ip, max_requests)

    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please try again later.",
            headers={"X-RateLimit-Remaining": str(remaining)}
        )
    return remaining
