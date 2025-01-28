import logging
from ollama import chat
from ollama import ChatResponse

from app.core.config import settings


class ResponseGenerator:

    @staticmethod
    async def generate_response(question: str, context: str) -> str:
        try:
            response: ChatResponse = chat(
                model=settings.MODEL_NAME_LLM,
                messages=[
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
                    {"role": "user", "content": f"Question: {question}"}
                ],
                options={
                    "temperature": 0.5,
                    "max_tokens": 200
                }
            )

            return response.message.content.strip()

        except Exception as e:
            logging.error(f"Erro na geração de resposta: {e}")
            return "Não foi possível gerar uma resposta no momento."
