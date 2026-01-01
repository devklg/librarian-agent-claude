from typing import List, Dict, Any, Optional

class PostgresClient:
    def __init__(self, url: str = None):
        self.url = url
        self.pool = None

    async def connect(self):
        if self.url:
            try:
                import asyncpg
                self.pool = await asyncpg.create_pool(self.url)
            except Exception as e:
                print(f"PostgreSQL connection failed: {e}")

    async def close(self):
        if self.pool:
            await self.pool.close()

    async def execute(self, query: str, *args) -> str:
        if not self.pool:
            return ""
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)

    async def fetch(self, query: str, *args) -> List[Dict]:
        if not self.pool:
            return []
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, *args)
            return [dict(row) for row in rows]

    async def fetchone(self, query: str, *args) -> Optional[Dict]:
        if not self.pool:
            return None
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, *args)
            return dict(row) if row else None
