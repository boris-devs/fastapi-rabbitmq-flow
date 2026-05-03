from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
from src.db import get_db
from src.repositories.users_repo import UserRepository
from src.security.token_manager import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(
		token: str = Depends(oauth2_scheme),
		db: AsyncSession = Depends(get_db)
):
	"""
	Fetches the current authenticated user based on the provided token and database session.

	Decodes the access token to retrieve the user ID, then queries the database to fetch the
	corresponding user. If the token is invalid, expired, or the user cannot be found, an
	HTTP 401 Unauthorized exception will be raised.

	:param token: The OAuth2 access token used to authenticate the user.
	:param db: The asynchronous database session used to query user information.
	:return: An instance of the authenticated user.
	:rtype: User
	:raises HTTPException: If token validation fails or the user does not exist.
	"""
	credentials_exception = HTTPException(
		status_code=status.HTTP_401_UNAUTHORIZED,
		detail="Could not validate credentials",
		headers={"WWW-Authenticate": "Bearer"},
	)

	repository = UserRepository(db)
	try:
		payload = decode_access_token(token)
		sub = payload.get("sub")
		if not sub:
			raise credentials_exception
		user_id = int(sub)
	except (ValueError, AttributeError, Exception) as e:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Could not validate credentials {e}")

	user = await repository.get_user_by_id(user_id)

	if user is None:
		raise credentials_exception

	return user
