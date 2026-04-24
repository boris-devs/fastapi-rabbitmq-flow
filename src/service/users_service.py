from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from src.security.passwords import verify_password
from src.security.token_manager import create_access_token
from src.repositories.users_repo import UserRepository
from src.schemas.users import UserCreateRequestSchema, UserLoginRequestSchema
from fastapi import status

from src.security.passwords import hash_password


class UserService:
	def __init__(self, user_repo: UserRepository):
		self.user_repo = user_repo

	async def register_new_user(self, data: UserCreateRequestSchema):
		exist_user = await self.user_repo.get_user_by_username_or_email(data.username, data.email)
		if exist_user:
			message = (
				"User with email already exists."
				if exist_user.email == data.email
				else "User with this username already exists."
			)
			raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
			                    detail=message)
		try:
			new_user = await self.user_repo.create(username=data.username,
			                                       email=data.email,
			                                       password_hash=hash_password(data.password))
			await self.user_repo.db.commit()
			return new_user
		except IntegrityError:
			await self.user_repo.db.rollback()
			raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
			                    detail="Something went wrong. Try one more late.")
		except Exception as e:
			await self.user_repo.db.rollback()
			raise e

	async def login_user(self, data: UserLoginRequestSchema):
		user = await self.user_repo.get_user_by_email(data.email)
		if not user:
			raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
		if not verify_password(data.password, user.password_hash):
			raise HTTPException(
				status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password"
			)
		access_token = create_access_token(data={"sub": str(user.id)})
		refresh_token = create_access_token(data={"sub": str(user.id)})
		return {"access_token": access_token,
		        "refresh_token": refresh_token,
		        "token_type": "bearer"
		        }
