from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from src.repositories.users_repo import UserRepository
from src.schemas.users import UserCreateRequestSchema, UserLoginSchema
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

	async def login_user(self, data: UserLoginSchema):
		user = await self.user_repo.get_user_by_email_and_pswd(data.email, data.password)
		if not user:
			raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
		return user