from typing import List, Dict, Any, Optional

class MongoDBClient:
    def __init__(self, url: str = None):
        self.url = url
        self.client = None
        self.db = None

    async def connect(self):
        if self.url:
            try:
                from motor.motor_asyncio import AsyncIOMotorClient
                self.client = AsyncIOMotorClient(self.url)
                self.db = self.client.librarian
            except Exception as e:
                print(f"MongoDB connection failed: {e}")

    async def store_document(self, document: Dict) -> Optional[str]:
        if not self.db:
            return None
        result = await self.db.documents.insert_one(document)
        return str(result.inserted_id)

    async def find_documents(self, query: Dict, limit: int = 10) -> List[Dict]:
        if not self.db:
            return []
        cursor = self.db.documents.find(query).limit(limit)
        return await cursor.to_list(length=limit)

    async def get_document(self, doc_id: str) -> Optional[Dict]:
        if not self.db:
            return None
        return await self.db.documents.find_one({"_id": doc_id})
