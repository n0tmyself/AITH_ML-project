import os
from celery import Celery
from ..ml.utils import generate_text

app_celery = Celery(
    'billing',
    broker=os.getenv('BROKER', 'redis://redis:6379/0'),
    backend=os.getenv('BACKEND', 'redis://redis:6379/1'),
)

@app_celery.task
def generate_text_task(prompt: str, tariff: str) -> str:
    return generate_text(prompt, tariff)
