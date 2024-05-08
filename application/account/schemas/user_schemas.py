from pydantic import BaseModel, ConfigDict, alias_generators, Field


class UserReadSchema(BaseModel):
    model_config = ConfigDict(alias_generator=alias_generators.to_camel, populate_by_name=True,
                              arbitrary_types_allowed=True, from_attributes=True)

    id: int = Field(validation_alias='tg_id')
    username: str
    first_name: str | None = ''
    last_name: str | None = ''
    is_active: bool
    stack: list[str] | None = []
    image: bytes | None = None
    city: str | None = ''
    description: str | None = ''


class UserCreateSchema(BaseModel):
    model_config = ConfigDict(alias_generator=alias_generators.to_camel, populate_by_name=True,
                              arbitrary_types_allowed=True, from_attributes=True)

    id: int = Field(validation_alias='tg_id')
    username: str | None = ''
    first_name: str | None = ''
    last_name: str | None = ''


class UserUpdateSchema(BaseModel):
    model_config = ConfigDict(alias_generator=alias_generators.to_camel, populate_by_name=True,
                              arbitrary_types_allowed=True, from_attributes=True)

    stack: list[str] | None = []
    city: str | None = ''
    description: str | None = ''
    image: bytes | None = None


class UserInDBSchema(UserReadSchema):
    hashed_password: str
