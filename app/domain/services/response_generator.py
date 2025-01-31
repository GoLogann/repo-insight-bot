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
        """
        Generate a chat response for a given user query using the context provided.

        This asynchronous method processes a user's question by adding it to the session history,
        constructs a message list for the AI model, and generates a response using the specified model.
        The response is then added to the session history.

        Args:
            user_id (str): The unique identifier of the user.
            question (str): The user's question to be answered.
            context (str): Additional context to assist in generating an accurate response.

        Returns:
            List[Dict[str, str]]: The updated chat history including the user's question and the AI's response.
        """
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
                    "temperature": 0,
                    "max_tokens": 200
                }
            )

            self.session_manager.add_message(user_id, "assistant", response.message.content)

            return self.session_manager.get_history(user_id)

        except Exception as e:
            logging.error(f"Error generating response: {e}")
            return []