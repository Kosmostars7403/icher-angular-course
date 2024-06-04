from pydantic import BaseModel, ConfigDict, alias_generators


class Token(BaseModel):
    # model_config = ConfigDict(alias_generator=alias_generators.to_camel, populate_by_name=True,
    #                           arbitrary_types_allowed=True, from_attributes=True)

    access_token: str
    refresh_token: str | None = None
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class RefreshToken(BaseModel):
    refresh_token: str
