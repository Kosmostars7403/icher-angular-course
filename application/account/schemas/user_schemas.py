from pydantic import BaseModel, ConfigDict, alias_generators, Field


class UserReadSchema(BaseModel):
    model_config = ConfigDict(alias_generator=alias_generators.to_camel, populate_by_name=True,
                              arbitrary_types_allowed=True, from_attributes=True)

    id: int = Field(validation_alias='tg_id')
    username: str
    name: str | None = None
    last_name: str | None = None
    is_active: bool | None = None
    stack: list[str] | None = []
    image: bytes | None = None
    city: str | None = None
    description: str | None = None


class UserCreateSchema(BaseModel):
    model_config = ConfigDict(alias_generator=alias_generators.to_camel, populate_by_name=True,
                              arbitrary_types_allowed=True, from_attributes=True)

    id: int = Field(validation_alias='tg_id')
    username: str | None = None
    name: str | None = None
    last_name: str | None = None


class UserUpdateSchema(BaseModel):
    model_config = ConfigDict(alias_generator=alias_generators.to_camel, populate_by_name=True,
                              arbitrary_types_allowed=True, from_attributes=True)

    stack: list[str] | None = []
    city: str | None = None
    description: str | None = None
    image: bytes | None = None


class UserInDBSchema(UserReadSchema):
    hashed_password: str
