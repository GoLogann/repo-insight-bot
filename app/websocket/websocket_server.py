import json
import logging
from fastapi import WebSocket


class WebSocketServer:
    def __init__(self, redis_service, rabbitmq_service):
        self.active_connections = set()
        self.redis_service = redis_service
        self.rabbitmq_service = rabbitmq_service

    async def websocket_handler(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logging.info("Nova conexão WebSocket aceita.")

        try:
            data = await websocket.receive_text()
            logging.info(f"Mensagem inicial recebida: {data}")

            try:
                request_data = json.loads(data)
                user_id = request_data.get("user_id")
                question = request_data.get("question")
                repo_url = request_data.get("repo_url")

                if not user_id or not question or not repo_url:
                    raise ValueError("Campos user_id, question ou repo_url ausentes na mensagem inicial.")
            except Exception as e:
                logging.error(f"Erro ao extrair dados da mensagem: {e}")
                await websocket.send_text(json.dumps({"error": "Dados inválidos ou ausentes na mensagem inicial."}))
                return

            # chat_history = self.redis_service.get_history(user_id)
            # if chat_history:
            #     logging.info(f"Histórico encontrado para o usuário {user_id}.")
            #
            #
            #     await self.rabbitmq_service.publish(
            #         "chat_responses",
            #         json.dumps({"history": chat_history})
            #     )
            #     logging.info("Histórico adicionado à fila 'chat_responses'.")

            while True:
                data = await websocket.receive_text()
                logging.info(f"Mensagem recebida: {data}")

                await self.rabbitmq_service.publish("chat_requests", data)
                logging.info("Mensagem publicada na fila 'chat_requests'.")

                async for response in self.rabbitmq_service.consume("chat_responses"):
                    await websocket.send_text(response)
                    logging.info(f"Resposta enviada para o front-end: {response}")
                    # break
        except Exception as e:
            logging.error(f"Erro na conexão WebSocket: {e}")
        finally:
            self.active_connections.remove(websocket)
            await websocket.close()
            logging.info("Conexão WebSocket encerrada.")