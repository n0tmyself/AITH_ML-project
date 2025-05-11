import json
import aio_pika
from infra.message_broker.connection import RabbitMQConnection
from infra.message_broker.schemas import BillingEvent
from core.use_cases.billing_use_cases import BillingService
from config.settings import settings

class RabbitMQConsumer:
    def __init__(self, connection: RabbitMQConnection, billing_use_cases: BillingService):
        self.connection = connection
        self.billing_use_cases = billing_use_cases

    async def consume_text_generation_tasks(self):
        """Слушает задачи на генерацию текста."""
        await self._consume(
            queue_name=settings.RABBITMQ_TEXT_GEN_QUEUE,
            exchange="text_generation_exchange",
            callback=self._handle_text_generation_task,
        )

    async def consume_billing_events(self):
        """Слушает события биллинга."""
        await self._consume(
            queue_name=settings.RABBITMQ_BILLING_QUEUE,
            exchange="billing_exchange",
            callback=self._handle_billing_event,
        )

    async def _consume(self, queue_name: str, exchange: str, callback):
        """Общий метод для подписки на очередь."""
        if not self.connection.channel:
            await self.connection.connect()

        # Создаем exchange и очередь
        exchange = await self.connection.channel.declare_exchange(
            exchange,
            aio_pika.ExchangeType.DIRECT,
            durable=True,
        )
        queue = await self.connection.channel.declare_queue(
            queue_name,
            durable=True,
        )
        await queue.bind(exchange, queue_name)

        # Начинаем слушать очередь
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    try:
                        data = json.loads(message.body.decode())
                        await callback(data)
                    except Exception as e:
                        print(f"Ошибка обработки сообщения: {e}")

    async def _handle_text_generation_task(self, task_data: dict):
        """Обрабатывает задачу генерации текста."""
        # Здесь логика вызова ML-модели
        print(f"Обработка задачи генерации: {task_data}")

        # После генерации отправляем событие в биллинг
        billing_event = BillingEvent(
            user_id=task_data["user_id"],
            task_id=task_data["task_id"],
            credits_used=10,  # Пример: списание 10 кредитов
            success=True,
        )
        await self.producer.send_billing_event(billing_event)

    async def _handle_billing_event(self, event_data: dict):
        """Обрабатывает событие биллинга."""
        await self.billing_use_cases.deduct_credits(
            user_id=event_data["user_id"],
            amount=event_data["credits_used"],
        )