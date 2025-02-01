import aio_pika
import logging

class RabbitMQService:
    def __init__(self):
        self.connection = None

    async def connect(self):
        try:
            self.connection = await aio_pika.connect_robust("amqp://rabbitmq:rabbitmq@localhost:5672/")
            logging.info("Conectado ao RabbitMQ.")
        except Exception as e:
            logging.error(f"Erro ao conectar ao RabbitMQ: {e}")
            raise

    async def close(self):
        if self.connection:
            await self.connection.close()
            logging.info("Conexão com o RabbitMQ fechada.")

    async def publish(self, queue_name: str, message: str):
        async with self.connection.channel() as channel:
            await channel.default_exchange.publish(
                aio_pika.Message(body=message.encode()),
                routing_key=queue_name,
            )
            logging.info(f"Mensagem publicada na fila {queue_name}.")

    async def consume(self, queue_name: str):
        async with self.connection.channel() as channel:
            queue = await channel.declare_queue(queue_name, durable=True)
            async for message in queue:
                async with message.process():
                    yield message.body.decode()
