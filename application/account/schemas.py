from pydantic import BaseModel, ConfigDict


class Token(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class UserReadSchema(BaseModel):
    id: int
    tg_id: int
    username: str
    name: str | None = None
    last_name: str | None = None
    is_active: bool | None = None
    stack: list[str] | None = []
    image: bytes | None = None
    city: str | None = None
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)


class UserCreateSchema(BaseModel):
    tg_id: int
    username: str
    password: str
    name: str | None = None
    last_name: str | None = None
    is_active: bool | None = None
    stack: list[str] | None = []
    city: str | None = None
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)


class UserUpdateSchema(BaseModel):
    password: str | None = None
    stack: list[str] | None = []
    city: str | None = None
    description: str | None = None
    image: bytes | None = None

    model_config = ConfigDict(from_attributes=True)


class UserInDBSchema(UserReadSchema):
    hashed_password: str
