from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

DATABASE_URL = "sqlite:///./billing.db"

class Settings(BaseSettings):
    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"
    RABBITMQ_TEXT_GEN_QUEUE: str = "text_generation_tasks"
    RABBITMQ_BILLING_QUEUE: str = "billing_events"
    RABBITMQ_PREFETCH_COUNT: int = 10

settings = Settings()

class Config(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=False)


class LogConfig(Config):
    model_config = SettingsConfigDict(case_sensitive=False, env_prefix="log_")
    level: str = "INFO"
    datetime_format: str = "%Y-%m-%d %H:%M:%S"


class ServiceConfig(Config):
    service_name: str = "recomendation_service"
    k_recs: int = 10
    model_names: List[str] = ["lightFM"]

    log_config: LogConfig


def get_config() -> ServiceConfig:
    return ServiceConfig(
        log_config=LogConfig(),
    )
