from app.infrastructure.openai.embedding_client import OpenAIEmbeddingClient

class EmbeddingService:
    def __init__(self, embedding_client: OpenAIEmbeddingClient):
        self.embedding_client = embedding_client

    def generate_embeddings(self, chunks):
        return [self.embedding_client.embed(chunk) for chunk in chunks]