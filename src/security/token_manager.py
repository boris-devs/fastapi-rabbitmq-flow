from datetime import timedelta, timezone, datetime

import jwt

from config import settings


def _create_token(data: dict, additional_claims: dict, secret: str, expires_delta: timedelta) -> str:
	"""
	Creates a JSON Web Token (JWT) using the provided data, additional claims, secret,
	and expiration delta. This function generates the token payload by combining the input
	data, additional claims, and an expiration timestamp, then encodes it using the specified
	secret and algorithm.

	:param data: Core payload data to include in the token.
	:param additional_claims: Additional claims to merge into the token payload.
	:param secret: Secret key used to sign the token.
	:param expires_delta: Duration after which the token will expire.
	:return: Encoded JWT as a string.
	"""
	to_encode = data.copy()
	expire = datetime.now(timezone.utc) + expires_delta
	to_encode.update(additional_claims)
	to_encode.update({"exp": expire})
	encoded_jwt = jwt.encode(to_encode, secret, algorithm=settings.ALGORITHM)
	return encoded_jwt


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
	"""
	Creates a new access token signed with a secret key and adds expiration details.

	This function generates a JWT (JSON Web Token) access token by encoding input data.
	It accepts additional options such as expiration time, which defaults to the
	duration set in the application settings. The token is signed with the secret key
	defined in the application settings.

	:param data: A dictionary containing the data to encode into the token.
	:param expires_delta: The time duration until the token expires. Defaults to
	    the application's access token expiration time if not provided.
	:return: A signed JWT access token as a string.
	"""
	return _create_token(data, {"type": "access"}, settings.ACCESS_SECRET_KEY,
	                     expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))

def create_refresh_token(data: dict, expires_delta: timedelta | None = None) -> str:
	"""
	Create a new refresh token for the given data.

	This function generates a refresh token by signing the provided data with a secret
	key and an optional expiration time. The token uses the "refresh" type and is
	primarily intended to facilitate secure session management.

	:param data: Information to include in the token payload. Typically, this includes
	    user identification details or other relevant claim data.
	:param expires_delta: Optional time delta that specifies the token's expiration
	    time. If not provided, the default expiration time configured by
	    `REFRESH_TOKEN_EXPIRE_DAYS` is used.
	:return: An encoded string representing the signed refresh token.
	"""
	return _create_token(data, {"type": "refresh"}, settings.REFRESH_SECRET_KEY,
	                     expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))