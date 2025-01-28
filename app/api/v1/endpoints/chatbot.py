from fastapi import APIRouter, HTTPException
from app.domain.schema.query import QueryRequest
from app.domain.schema.response_schema import ResponseSchema
from app.domain.services.document_processor import DocumentProcessor
from app.domain.services.embedding_service import EmbeddingService
from app.domain.services.response_generator import ResponseGenerator
from app.domain.services.retriever import DocumentRetriever
from app.infrastructure.qdrant.store import QdrantVectorStore
from app.infrastructure.github.pydriller_client import PyDrillerClient
from app.infrastructure.sentence_transformers.embedding_client import SentenceTransformersEmbeddingClient

router = APIRouter()

@router.post(path="/repo-insight-bot/ask", response_model=ResponseSchema)
async def ask_question(request: QueryRequest):
    try:
        document_processor = DocumentProcessor()
        embedding_service = EmbeddingService(SentenceTransformersEmbeddingClient())
        vector_store = QdrantVectorStore()
        retriever = DocumentRetriever(vector_store)
        response_generator = ResponseGenerator()

        repo_data = PyDrillerClient().fetch_repository_data(request.repo_url)

        chunks = document_processor.process_repository_data(repo_data)
        chunk_embeddings = embedding_service.generate_embeddings(chunks)

        vector_store.save(repo_url=request.repo_url, chunks=chunks, chunk_embeddings=chunk_embeddings)

        query_embedding = embedding_service.embedding_client.embed(request.question)

        relevant_docs = retriever.retrieve_relevant_documents(request.repo_url, query_embedding)

        response = await response_generator.generate_response(request.question, relevant_docs)

        return ResponseSchema(response=response)

    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
