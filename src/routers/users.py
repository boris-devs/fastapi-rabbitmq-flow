from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.db import get_db
from src.repositories.users_repo import UserRepository
from src.schemas.users import (UserCreateRequestSchema, UserCreateResponseSchema, UserLoginRequestSchema,
                               UserLoginResponseSchema)
from src.service.users_service import UserService

router = APIRouter()


def user_service(db: AsyncSession = Depends(get_db)):
	user_repo = UserRepository(db)
	service = UserService(user_repo)
	return service


@router.post("/register/", response_model=UserCreateResponseSchema)
async def register_user(user_data: UserCreateRequestSchema, service: UserService = Depends(user_service)):
	return await service.register_new_user(user_data)


@router.post("/login/", response_model=UserLoginResponseSchema)
async def login(user_data: UserLoginRequestSchema, service: UserService = Depends(user_service)):
	return await service.login_user(user_data)
