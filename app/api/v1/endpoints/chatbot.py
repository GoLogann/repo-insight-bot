from fastapi import APIRouter, HTTPException

from app.domain.schema.query import QueryRequest
from app.infrastructure.github.pydriller_client import PyDrillerClient
from app.domain.services.document_processor import DocumentProcessor
from app.domain.services.embedding_service import EmbeddingService
from app.domain.services.retriever import DocumentRetriever
from app.domain.services.response_generator import ResponseGenerator
from app.infrastructure.chroma.store import ChromaVectorStore
from app.infrastructure.openai.embedding_client import OpenAIEmbeddingClient

router = APIRouter()

@router.post("/repo-insight-bot/ask")
async def ask_question(request: QueryRequest):
    try:
        repo_data = PyDrillerClient().fetch_repository_data(request.repo_url)

        processor = DocumentProcessor()
        chunks = processor.process_repository_data(repo_data)

        embedding_service = EmbeddingService(OpenAIEmbeddingClient())
        chunk_embeddings = embedding_service.generate_embeddings(chunks)

        vector_store = ChromaVectorStore()
        vector_store.save(chunks, chunk_embeddings)

        query_embedding = embedding_service.embedding_client.embed(request.question)
        retriever = DocumentRetriever(vector_store)
        relevant_docs = retriever.retrieve_relevant_documents(query_embedding)

        generator = ResponseGenerator()
        response = generator.generate_response(request.question, relevant_docs)
        return {"response": response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
