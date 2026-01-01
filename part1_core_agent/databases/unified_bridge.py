from typing import Dict, Any, List, Optional
from .chromadb_client import ChromaDBClient
from .mongodb_client import MongoDBClient
from .neo4j_client import Neo4jClient
from .postgres_client import PostgresClient

class UniversalMemoryBridge:
    def __init__(self, config: Dict[str, str] = None):
        config = config or {}
        self.chroma = ChromaDBClient(config.get('chromadb_url'))
        self.mongo = MongoDBClient(config.get('mongodb_url'))
        self.neo4j = Neo4jClient(config.get('neo4j_url'), config.get('neo4j_user'), config.get('neo4j_password'))
        self.postgres = PostgresClient(config.get('postgres_url'))
        self._connected = False

    async def connect_all(self):
        await self.chroma.connect()
        await self.mongo.connect()
        await self.neo4j.connect()
        await self.postgres.connect()
        self._connected = True

    async def close_all(self):
        await self.neo4j.close()
        await self.postgres.close()

    async def search(self, query: str, n_results: int = 5, category: str = "all") -> Dict[str, Any]:
        vector_results = await self.chroma.search(query, n_results)
        mongo_filter = {"category": category} if category != "all" else {}
        doc_results = await self.mongo.find_documents(mongo_filter, n_results)
        graph_results = await self.neo4j.query_relationships(query, depth=1)

        return {
            "semantic": vector_results,
            "documents": doc_results,
            "relationships": graph_results,
            "total_sources": len(vector_results) + len(doc_results)
        }

    async def ingest(self, content: str, metadata: Dict, doc_id: str):
        await self.chroma.add_documents([content], [metadata], [doc_id])
        await self.mongo.store_document({"_id": doc_id, "content": content, "metadata": metadata})
