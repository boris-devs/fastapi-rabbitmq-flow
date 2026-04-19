from fastapi import FastAPI
from src.config import settings
app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": settings.POSTGRES_DATABASE_URL}
