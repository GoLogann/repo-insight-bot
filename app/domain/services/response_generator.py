from openai import OpenAI
from app.core.config import settings

class ResponseGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def generate_response(self, question, context):
        prompt = f"""
        You are an Al assistant for a software repository QA task, use the following pieces of context to answer
        the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an 
        answer. Use three sentences maximum. Keep the answer as concise as possible.
        Context: {context}
        Question: {question}
        """
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content