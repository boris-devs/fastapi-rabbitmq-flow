from pydantic import BaseModel


class UserBaseSchema(BaseModel):
	username: str
	email: str


class UserCreateRequestSchema(UserBaseSchema):
	password: str


class UserCreateResponseSchema(UserBaseSchema):
	id: int


class UserLoginRequestSchema(BaseModel):
	email: str
	password: str


class UserLoginResponseSchema(BaseModel):
	access_token: str
	refresh_token: str
	token_type: str = "bearer"
