import logging
from typing import List, Dict

from ollama import chat
from ollama import ChatResponse

from app.core.config import settings
from app.domain.services.session_manager import SessionManager


class ResponseGenerator:
    def __init__(self):
        self.session_manager = SessionManager()

    async def generate_response(self, user_id: str, question: str, context: str) -> List[Dict[str, str]]:
        try:
            self.session_manager.add_message(user_id, "user", question)

            history = self.session_manager.get_history(user_id)

            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are an AI assistant for a software repository QA task. "
                        "Use the provided context to answer precisely. "
                        "If no clear answer exists, state 'I cannot find sufficient information'. "
                        "Be concise and direct, using maximum three sentences."
                    )
                },
                {"role": "system", "content": f"Context: {context}"},
            ]
            messages.extend(history)

            response: ChatResponse = chat(
                model=settings.MODEL_NAME_LLM,
                messages=messages,
                options={
                    "temperature": 0.5,
                    "max_tokens": 200
                }
            )

            self.session_manager.add_message(user_id, "assistant", response.message.content)

            return self.session_manager.get_history(user_id)

        except Exception as e:
            logging.error(f"Error generating response: {e}")
            return []