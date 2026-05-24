from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.broker.rabbitmq_manager import RabbitMQManager
from src.config import settings
from src.routers import users_router, healthcheck_router


@asynccontextmanager
async def lifespan(app: FastAPI):
	rmq_manager = RabbitMQManager(settings.RABBITMQ_AMQP_URL)
	await rmq_manager.connect()
	app.state.rmq_manager = rmq_manager
	yield
	await rmq_manager.close()


app = FastAPI(lifespan=lifespan)

prefix = "/api"
app.include_router(router=users_router, prefix=f"{prefix}/users", tags=["users"])
app.include_router(router=healthcheck_router, prefix=f"/healthcheck", tags=["healthcheck"])