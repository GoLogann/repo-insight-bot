import socketio
import logging

from app.domain.schema.chat_response import ChatResponseSchema, AnswerAndQuestionSchema
from app.domain.schema.query import QueryRequest
from app.domain.services.document_processor import DocumentProcessor
from app.domain.services.embedding_service import EmbeddingService
from app.domain.services.response_generator import ResponseGenerator
from app.domain.services.retriever import DocumentRetriever
from app.domain.services.session_manager import SessionManager
from app.infrastructure.qdrant.store import QdrantVectorStore
from app.infrastructure.github.pydriller_client import PyDrillerClient
from app.infrastructure.sentence_transformers.embedding_client import SentenceTransformersEmbeddingClient

document_processor = DocumentProcessor()
embedding_service = EmbeddingService(SentenceTransformersEmbeddingClient())
vector_store = QdrantVectorStore()
retriever = DocumentRetriever(vector_store)
response_generator = ResponseGenerator()
session_manager = SessionManager()

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")

@sio.event
async def connect(sid, environ):
    logging.info(f"Client connected: {sid}")

@sio.event
async def disconnect(sid):
    logging.info(f"Client disconnected: {sid}")

@sio.event
async def ask_question(sid, data):
    try:
        request = QueryRequest(**data)

        if not session_manager.get_history(request.user_id):
            session_manager.create_session(request.user_id)
            logging.info(f"New session created for user_id: {request.user_id}")

        repo_data = PyDrillerClient().fetch_repository_data(request.repo_url)

        chunks = document_processor.process_repository_data(repo_data)
        chunk_embeddings = embedding_service.generate_embeddings(chunks)

        vector_store.save(repo_url=request.repo_url, chunks=chunks, chunk_embeddings=chunk_embeddings)

        query_embedding = embedding_service.embedding_client.embed(request.question)

        relevant_docs = retriever.retrieve_relevant_documents(request.repo_url, query_embedding)

        chat_history = await response_generator.generate_response(request.user_id, request.question, relevant_docs)

        formatted_history = [
            AnswerAndQuestionSchema(question=msg["content"], answer=next_msg["content"])
            for msg, next_msg in zip(chat_history[::2], chat_history[1::2])
            if msg["role"] == "user" and next_msg["role"] == "assistant"
        ]

        await sio.emit("response", ChatResponseSchema(chat_history=formatted_history).dict(), to=sid)

    except Exception as e:
        logging.error(f"Error processing question: {e}")
        await sio.emit("error", {"detail": str(e)}, to=sid)