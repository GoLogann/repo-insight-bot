from fastapi import APIRouter
from app.api.v1.endpoints import chatbot, extract

router = APIRouter()

router.include_router(chatbot.chat)
router.include_router(extract.app)