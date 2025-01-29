from pydantic import BaseModel
from typing import List

class AnswerAndQuestionSchema(BaseModel):
    question: str
    answer: str

class ChatResponseSchema(BaseModel):
    chat_history: List[AnswerAndQuestionSchema]