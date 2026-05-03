from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from src.broker.constants import USER_REGISTRATION_QUEUE
from src.broker.rabbitmq_manager import RabbitMQManagerInterface
from src.security.passwords import verify_password
from src.security.token_manager import create_access_token
from src.repositories.users_repo import UserRepository
from src.schemas.users import UserCreateRequestSchema, UserLoginRequestSchema
from fastapi import status

from src.security.passwords import hash_password


class UserService:
	def __init__(self, user_repo: UserRepository, rmq_manager: RabbitMQManagerInterface):
		self.user_repo = user_repo
		self.rmq_manager = rmq_manager

	async def register_new_user(self, data: UserCreateRequestSchema):
		"""
		Registers a new user in the database. Validates if a user with the given username or
		email already exists. If a user exists, raises an HTTP exception indicating the conflict.
		If the registration process encounters database issues or other errors, appropriate
		exceptions are raised.

		:param data: User creation details containing username, email, and password.
		:type data: UserCreateRequestSchema
		:return: The newly created user object if the registration succeeds.
		:rtype: User
		:raises HTTPException: If a user with the specified username or email already exists,
		    if a database integrity error occurs during the operation, or if another issue
		    is encountered.
		"""
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
			#message to broker with new user data
			user_data = {"user_id": new_user.id, "username": new_user.username, "email": new_user.email}
			await self.rmq_manager.publish(USER_REGISTRATION_QUEUE, message=user_data)
			return new_user
		except IntegrityError:
			await self.user_repo.db.rollback()
			raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
			                    detail="Something went wrong. Try one more late.")
		except Exception as e:
			await self.user_repo.db.rollback()
			raise e

	async def login_user(self, data: UserLoginRequestSchema):
		"""
		Authenticates the user using the provided email and password and generates
		access and refresh tokens upon successful login. This method validates
		the user's credentials, checks if the email exists, and ensures the
		provided password matches the stored password hash. Upon successful
		validation, it returns a dictionary containing the access token,
		refresh token, and token type.

		:param data: An instance of "UserLoginRequestSchema" containing the
		    user's login credentials, including email and password.
		:type data: UserLoginRequestSchema

		:return: A dictionary containing the generated access token, refresh
		    token, and token type.
		:rtype: dict

		:raises HTTPException: If the user does not exist or the provided email
		    and password do not match, raises an HTTP 401 error indicating
		    unauthorized access.

		"""
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

	async def user_profile(self, user_id: int):
		user = await self.user_repo.get_user_by_id(user_id)
		if not user:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
		return user
