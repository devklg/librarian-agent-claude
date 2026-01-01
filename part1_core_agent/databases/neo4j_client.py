from typing import List, Dict, Any

class Neo4jClient:
    def __init__(self, url: str = None, user: str = None, password: str = None):
        self.url = url
        self.user = user
        self.password = password
        self.driver = None

    async def connect(self):
        if self.url and self.user and self.password:
            try:
                from neo4j import AsyncGraphDatabase
                self.driver = AsyncGraphDatabase.driver(self.url, auth=(self.user, self.password))
            except Exception as e:
                print(f"Neo4j connection failed: {e}")

    async def close(self):
        if self.driver:
            await self.driver.close()

    async def add_relationship(self, source: str, target: str, rel_type: str, properties: Dict = None):
        if not self.driver:
            return None
        query = """
        MERGE (a:Entity {name: $source})
        MERGE (b:Entity {name: $target})
        MERGE (a)-[r:RELATES {type: $rel_type}]->(b)
        SET r += $props
        RETURN a, r, b
        """
        async with self.driver.session() as session:
            await session.run(query, source=source, target=target, rel_type=rel_type, props=properties or {})

    async def query_relationships(self, entity: str, depth: int = 2) -> List[Dict]:
        if not self.driver:
            return []
        query = "MATCH path = (e:Entity {name: $entity})-[*1..$depth]-(related) RETURN path LIMIT 50"
        async with self.driver.session() as session:
            result = await session.run(query, entity=entity, depth=depth)
            return await result.data()
