from contextlib import asynccontextmanager

from fastapi import FastAPI

from broker.rabbitmq_manager import RabbitMQManager
from src.config import settings
from src.routers import users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
	pika_connection = RabbitMQManager(settings.RABBITMQ_AMQP_URL)
	await pika_connection.connect()
	app.state.rmq = pika_connection
	yield
	await pika_connection.close()


app = FastAPI(lifespan=lifespan)

prefix = "/api"
app.include_router(router=users_router, prefix=f"{prefix}/users", tags=["users"])
