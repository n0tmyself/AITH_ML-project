import uvicorn
from fastapi import FastAPI
from infra.web.controllers import billing_controller, user_controller
from infra.db.database import engine
from infra.db.models import Base, BillingAccountModel
from infra.message_broker.connection import RabbitMQConnection
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Подключение к RabbitMQ при старте
    rabbit_connection = RabbitMQConnection()
    await rabbit_connection.connect()
    app.state.rabbit_connection = rabbit_connection
    
    yield  # Здесь работает приложение
    
    # Закрытие подключения при остановке
    await rabbit_connection.close()

app = FastAPI(lifespan=lifespan)

Base.metadata.create_all(bind=engine)
app.include_router(billing_controller.router)
app.include_router(user_controller.router)



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
