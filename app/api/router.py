from fastapi import APIRouter
from app.api.v1.endpoints import chatbot

router = APIRouter()

router.include_router(chatbot.router)