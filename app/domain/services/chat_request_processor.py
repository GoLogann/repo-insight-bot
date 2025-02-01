import logging
from app.domain.schema.chat_response import ChatResponseSchema, AnswerAndQuestionSchema
from app.domain.schema.query import QueryRequest
from app.domain.services.document_processor import DocumentProcessor
from app.domain.services.embedding_service import EmbeddingService
from app.domain.services.response_generator import ResponseGenerator
from app.domain.services.retriever import DocumentRetriever
from app.domain.services.session_manager import SessionManager
from app.infrastructure.qdrant.store import QdrantVectorStore
from app.infrastructure.sentence_transformers.embedding_client import SentenceTransformersEmbeddingClient
from app.utils.helpers import is_repo_downloaded


class ChatRequestProcessor:
    def __init__(self):
        self.document_processor = DocumentProcessor()
        self.embedding_service = EmbeddingService(SentenceTransformersEmbeddingClient())
        self.vector_store = QdrantVectorStore()
        self.retriever = DocumentRetriever(self.vector_store)
        self.response_generator = ResponseGenerator()
        self.session_manager = SessionManager()

    async def process(self, request: QueryRequest) -> ChatResponseSchema:
        try:
            if not self.session_manager.get_history(request.user_id):
                self.session_manager.create_session(request.user_id)
                logging.info(f"New session created for user_id: {request.user_id}")

            repo_data = self._read_repository_data()
            if not is_repo_downloaded(request.repo_url):
                self._process_and_store_repository(request.repo_url, repo_data)

            query_embedding = self.embedding_service.embedding_client.embed(request.question)
            relevant_docs = self.retriever.retrieve_relevant_documents(request.repo_url, query_embedding)
            relevant_docs = " ".join(relevant_docs)

            chat_history = await self.response_generator.generate_response(
                request.user_id, request.question, relevant_docs
            )

            formatted_history = [
                AnswerAndQuestionSchema(question=msg["content"], answer=next_msg["content"])
                for msg, next_msg in zip(chat_history[::2], chat_history[1::2])
                if msg["role"] == "user" and next_msg["role"] == "assistant"
            ]

            return ChatResponseSchema(chat_history=formatted_history)

        except Exception as e:
            logging.error(f"Error processing chat request: {e}")
            return ChatResponseSchema(chat_history=[])

    @staticmethod
    def _read_repository_data() -> str:
        with open("/home/logan/TEES/repo-insight-bot/data/phishing-quest-api/repository_data.txt", "r") as file:
            return file.read()

    def _process_and_store_repository(self, repo_url: str, repo_data: str):
        chunks = self.document_processor.process_repository_data(repo_data)
        chunk_embeddings = self.embedding_service.generate_embeddings(chunks)
        self.vector_store.save(repo_url=repo_url, chunks=chunks, chunk_embeddings=chunk_embeddings)
