import aio_pika
from config.settings import settings
from infra.message_broker.schemas import TextGenerationTask, BillingEvent
from infra.message_broker.connection import RabbitMQConnection

class RabbitMQProducer:
    def __init__(self, connection: RabbitMQConnection):
        self.connection = connection

    async def send_text_generation_task(self, task: TextGenerationTask):
        """Отправляет задачу на генерацию текста."""
        await self._publish_message(
            exchange="text_generation_exchange",
            routing_key=settings.RABBITMQ_TEXT_GEN_QUEUE,
            message=task.model_dump_json(),
        )

    async def send_billing_event(self, event: BillingEvent):
        """Отправляет событие биллинга."""
        await self._publish_message(
            exchange="billing_exchange",
            routing_key=settings.RABBITMQ_BILLING_QUEUE,
            message=event.model_dump_json(),
        )

    async def _publish_message(self, exchange: str, routing_key: str, message: str):
        """Общий метод для публикации сообщений."""
        if not self.connection.channel:
            await self.connection.connect()

        # Создаем exchange (если его нет)
        exchange = await self.connection.channel.declare_exchange(
            exchange,
            aio_pika.ExchangeType.DIRECT,
            durable=True,  # Сохраняет сообщения при перезапуске RabbitMQ
        )

        # Отправляем сообщение
        await exchange.publish(
            aio_pika.Message(
                body=message.encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,  # Сохраняет сообщения на диске
            ),
            routing_key=routing_key,
        )