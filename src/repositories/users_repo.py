from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.users import Users


class UserRepository:
	def __init__(self, db_session: AsyncSession):
		self.db = db_session

	async def get_user_by_username_or_email(self, username: str, email: str):
		stmt = await self.db.execute(select(Users).where(or_(Users.username == username, Users.email == email)))
		result = stmt.scalars().first()
		return result

	async def create(self, username: str, email: str, password_hash: str) -> Users:
		new_user = Users(
			username=username,
			email=email,
			password_hash=password_hash
		)
		self.db.add(new_user)
		await self.db.flush()
		return new_user

	async def get_user_by_email(self, email: str) -> Users | None:
		user = await self.db.execute(select(Users).where(Users.email == email))
		result = user.scalar_one_or_none()
		return result

	async def get_user_by_id(self, user_id: int) -> Users | None:
		user = await self.db.execute(select(Users).where(Users.id == user_id))
		result = user.scalar_one_or_none()
		return result