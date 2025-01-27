import chromadb
from typing import List, Any

class ChromaVectorStore:
    def __init__(self, collection_name: str = "repository_docs"):
        self.client = chromadb.Client()
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def save(self, chunks: List[str], chunk_embeddings: List[List[float]]):
        ids = [f"doc_{i}" for i in range(len(chunks))]

        self.collection.add(
            embeddings=chunk_embeddings,
            documents=chunks,
            ids=ids
        )

    def query(self, query_embedding: List[float], top_k: int = 3) -> List[Any]:
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        return results['documents'][0]

    def get_all(self):
        results = self.collection.get(include=['documents', 'embeddings'])
        return results['embeddings'], results['documents']
