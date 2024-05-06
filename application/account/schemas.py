from pydantic import BaseModel, ConfigDict


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class UserReadSchema(BaseModel):
    tg_id: int
    username: str
    name: str | None = None
    last_name: str | None = None
    is_active: bool | None = None

    model_config = ConfigDict(from_attributes=True)


class UserCreateSchema(UserReadSchema):
    password: str


class UserInDBSchema(UserReadSchema):
    hashed_password: str
