import uuid
from typing import List, Any

from pydantic import BaseModel
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
from urllib.parse import urlparse

from app.core.config import settings

class Document(BaseModel):
    text: str
    embedding: List[float]

class QueryResponse(BaseModel):
    text: str

class QdrantVectorStore:
    def __init__(self):
        self.client = QdrantClient(url=settings.QDRANT_URL)

    @staticmethod
    def _extract_repo_name(repo_url: str) -> str:
        parsed_url = urlparse(repo_url)
        return parsed_url.path.strip("/").split("/")[-1]

    def save(self, repo_url: str, chunks: List[str], chunk_embeddings: List[List[float]]):
        collection_name = self._extract_repo_name(repo_url)

        if not self.client.collection_exists(collection_name):
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=len(chunk_embeddings[0]), distance=Distance.COSINE),
            )

        points = [
            PointStruct(id=str(uuid.uuid4()), vector=chunk_embeddings[i], payload={"text": chunks[i]})
            for i in range(len(chunks))
        ]
        self.client.upsert(collection_name=collection_name, points=points)

    def query(self, repo_url: str, query_embedding: List[float], top_k: int = 3) -> List[QueryResponse]:
        collection_name = self._extract_repo_name(repo_url)

        if not self.client.collection_exists(collection_name):
            raise ValueError(f"Collection '{collection_name}' not found. Did you forget to save it first?")

        search_result = self.client.search(
            collection_name=collection_name,
            query_vector=query_embedding,
            limit=top_k,
        )

        return [QueryResponse(text=hit.payload["text"]) for hit in search_result]

    def get_all(self, repo_url: str) -> List[Document]:
        collection_name = self._extract_repo_name(repo_url)

        if not self.client.collection_exists(collection_name):
            raise ValueError(f"Collection '{collection_name}' not found.")

        # Fetch points (documents) from the collection
        scroll_result = self.client.scroll(collection_name=collection_name)

        # Access the list of records from scroll_result[0]
        points = scroll_result[0]

        documents = []
        for point in points:
            # Ensure that the vector (embedding) is not None; if so, set it to an empty list
            vector = point.vector if point.vector is not None else []
            documents.append(Document(text=point.payload["text"], embedding=vector))

        return documents
