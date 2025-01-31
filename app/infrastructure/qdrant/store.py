import uuid
from typing import List
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
from app.core.config import settings
from app.domain.schema.document import Document
from app.domain.schema.query import QueryResponse
from app.utils.helpers import extract_repo_name


class QdrantVectorStore:
    def __init__(self):
        self.client = QdrantClient(url=settings.QDRANT_URL)

    def is_repo_processed(self, repo_url: str) -> bool:

        return self.client.collection_exists(extract_repo_name(repo_url))

    def save(self, repo_url: str, chunks: List[str], chunk_embeddings: List[List[float]]):
        """
        Saves the given chunks and chunk embeddings to the Qdrant collection for the given repository URL.

        Args:
            repo_url (str): The URL of the repository.
            chunks (List[str]): A list of strings containing the text of each chunk.
            chunk_embeddings (List[List[float]]): A list of lists of floats containing the embedding for each chunk.
        """
        collection_name = extract_repo_name(repo_url)

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
        """
        Queries the Qdrant collection for the given repository URL with the given query embedding.

        Args:
            repo_url (str): The URL of the repository.
            query_embedding (List[float]): The query embedding.
            top_k (int, optional): The number of top results to return. Defaults to 3.

        Returns:
            List[QueryResponse]: A list of QueryResponse objects containing the text of the top-k results.
        """
        collection_name = extract_repo_name(repo_url)

        if not self.client.collection_exists(collection_name):
            raise ValueError(f"Collection '{collection_name}' not found. Did you forget to save it first?")

        search_result = self.client.search(
            collection_name=collection_name,
            query_vector=query_embedding,
            limit=top_k,
        )

        return [QueryResponse(text=hit.payload["text"]) for hit in search_result]

    def get_all(self, repo_url: str) -> List[Document]:
        """
        Retrieves all documents from the Qdrant collection for the given repository URL.

        Args:
            repo_url (str): The URL of the repository.

        Returns:
            List[Document]: A list of Document objects, each containing the text of a document and the corresponding embedding.
        """
        collection_name = extract_repo_name(repo_url)

        if not self.client.collection_exists(collection_name):
            raise ValueError(f"Collection '{collection_name}' not found.")

        scroll_result = self.client.scroll(collection_name=collection_name)

        points = scroll_result[0]

        documents = []
        for point in points:
            vector = point.vector if point.vector is not None else []
            documents.append(Document(text=point.payload["text"], embedding=vector))

        return documents
