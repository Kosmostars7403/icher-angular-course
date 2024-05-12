from pydantic import BaseModel, ConfigDict, alias_generators


class Token(BaseModel):

    access_token: str
    refresh_token: str | None = None
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
