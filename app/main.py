import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.api.rest_router import router as api_router
from app.websocket.websocket_server import WebSocketServer
from app.domain.services.rabbitmq_service import RabbitMQService
from app.domain.services.session_manager import SessionManager
from workers.chat_worker import chat_worker

redis_service = SessionManager()
rabbitmq_service = RabbitMQService()
websocket_server = WebSocketServer(redis_service, rabbitmq_service)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await rabbitmq_service.connect()
    worker_task = asyncio.create_task(chat_worker(rabbitmq_service))

    yield

    await rabbitmq_service.close()

    worker_task.cancel()
    try:
        await worker_task
    except asyncio.CancelledError:
        pass
    finally:
        await rabbitmq_service.close()
app = FastAPI(
    title="Repo Insight Bot",
    version="0.0.1",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router)

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket_server.websocket_handler(websocket)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )