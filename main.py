from fastapi import FastAPI
from src.routers import users_router
app = FastAPI()


prefix = "/api"
app.include_router(router=users_router, prefix=f"{prefix}/users", tags=["users"])
