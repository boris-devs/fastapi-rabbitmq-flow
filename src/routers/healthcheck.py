from fastapi import APIRouter
from loguru import logger
router = APIRouter()

@router.get("/app")
async def healthcheck():
	logger.info("Healthcheck app service, status: OK")
	return {"status": "ok"}