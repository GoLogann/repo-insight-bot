import json
import logging
from app.domain.schema.query import QueryRequest
from app.domain.services.chat_request_processor import ChatRequestProcessor


async def chat_worker(rabbitmq_service):
    chat_processor = ChatRequestProcessor()

    async for message in rabbitmq_service.consume("chat_requests"):
        try:
            request_data = json.loads(message)
            request = QueryRequest(**request_data)

            response = await chat_processor.process(request)

            await rabbitmq_service.publish("chat_responses", json.dumps(response))

        except Exception as e:
            logging.error(f"Erro ao processar mensagem do RabbitMQ: {e}")