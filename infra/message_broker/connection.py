import aio_pika
from config.settings import settings

class RabbitMQConnection:
    def __init__(self):
        self.connection = None
        self.channel = None

    async def connect(self):
        self.connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
        self.channel = await self.connection.channel()
        await self.channel.set_qos(prefetch_count=settings.RABBITMQ_PREFETCH_COUNT)
        return self

    async def close(self):
        if self.connection:
            await self.connection.close()