from pydantic import BaseModel, ConfigDict, alias_generators, Field, field_validator


class UserReadSmallSchema(BaseModel):
    model_config = ConfigDict(alias_generator=alias_generators.to_camel, populate_by_name=True,
                              arbitrary_types_allowed=True, from_attributes=True)

    id: int = Field(validation_alias='tg_id')
    username: str
    avatar_url: str | None = None
    subscribers_amount: int | None = 0


class UserReadSchemaShort(UserReadSmallSchema):

    first_name: str | None = ''
    last_name: str | None = ''
    is_active: bool | None = True
    stack: list[str] | None = []
    city: str | None = ''
    description: str | None = ''

    @field_validator('description', mode='before')
    def get_150_symbols(cls, v):
        return v[:150] if v else ''


class SubscriptionsSchema(BaseModel):
    subscriptions: list[UserReadSchemaShort]


class UserReadSchema(UserReadSchemaShort):
    description: str | None = ''

    @field_validator('description', mode='before')
    def get_full_length(cls, v):
        return v


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

    first_name: str | None = None
    last_name: str | None = None
    stack: list[str] | None = None
    city: str | None = None
    description: str | None = None


class UserInDBSchema(UserReadSchema):
    hashed_password: str
