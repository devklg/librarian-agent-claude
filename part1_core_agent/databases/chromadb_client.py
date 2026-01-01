from typing import List, Dict, Any, Optional

class ChromaDBClient:
    def __init__(self, url: str = None):
        self.url = url
        self.client = None
        self.collection = None

    async def connect(self):
        if self.url:
            try:
                import chromadb
                self.client = chromadb.HttpClient(host=self.url.split("://")[1].split(":")[0])
                self.collection = self.client.get_or_create_collection("documentation")
            except Exception as e:
                print(f"ChromaDB connection failed: {e}")

    async def search(self, query: str, n_results: int = 5, where: Dict = None) -> List[Dict]:
        if not self.collection:
            return []
        try:
            results = self.collection.query(query_texts=[query], n_results=n_results, where=where)
            return [{"content": doc, "metadata": meta} for doc, meta in zip(results.get("documents", [[]])[0], results.get("metadatas", [[]])[0])]
        except:
            return []

    async def add_documents(self, documents: List[str], metadatas: List[Dict], ids: List[str]):
        if self.collection:
            self.collection.add(documents=documents, metadatas=metadatas, ids=ids)
