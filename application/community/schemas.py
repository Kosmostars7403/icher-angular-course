from datetime import datetime

from pydantic import BaseModel, ConfigDict, alias_generators, field_validator

from application.account.schemas.user_schemas import UserReadSchemaShort
from application.comment.schemas import CommentReadWithChildSchema
from application.community.models import CommunityThemes as CommunityTheme


class Theme(BaseModel):
    theme: CommunityTheme

class CommunityShortReadSchema(BaseModel):
    model_config = ConfigDict(alias_generator=alias_generators.to_camel, populate_by_name=True,
                              from_attributes=True)

    id: int
    admin: UserReadSchemaShort
    name: str
    themes: list[CommunityTheme] | None = []
    tags: list[str] | None = []
    banner_url: str | None = None
    avatar_url: str | None = None
    description: str | None = None
    subscribers_amount: int | None = 0
    created_at: datetime

class PostReadSchema(BaseModel):
    model_config = ConfigDict(alias_generator=alias_generators.to_camel, populate_by_name=True,
                              from_attributes=True)

    id: int
    title: str
    community_id: int | None = None
    content: str | None = ''
    author: UserReadSchemaShort | CommunityShortReadSchema
    images: list[str] | None = None
    created_at: datetime
    updated_at: datetime | None = None
    likes: int

    @field_validator('likes', mode='before')
    def validate_likes(cls, v):
        return len([like for like in v])

    comments: list[CommentReadWithChildSchema] | None = []

class CommunityReadSchema(CommunityShortReadSchema):
    posts: list[PostReadSchema] | None = []


class CommunityCreateSchema(BaseModel):
    model_config = ConfigDict(alias_generator=alias_generators.to_camel,
                              populate_by_name=True, from_attributes=True)

    name: str
    themes: list[CommunityTheme] | None = []
    tags: list[str] | None = []
    description: str | None = None


class CommunityUpdateSchema(BaseModel):
    model_config = ConfigDict(alias_generator=alias_generators.to_camel,
                              populate_by_name=True, from_attributes=True)

    name: str | None = None
    themes: list[CommunityTheme] | None = None
    tags: list[str] | None = None
    description: str | None = None


class SubscriptionsSchema(BaseModel):
    subscriptions: list[UserReadSchemaShort]
