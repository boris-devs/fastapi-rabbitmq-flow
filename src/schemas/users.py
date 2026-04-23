from pydantic import BaseModel


class UserBaseSchema(BaseModel):
    username: str
    email: str

class UserCreateRequestSchema(UserBaseSchema):
    password: str

class UserCreateResponseSchema(UserBaseSchema):
    id: int

class UserLoginSchema(BaseModel):
    email: str
    password: str