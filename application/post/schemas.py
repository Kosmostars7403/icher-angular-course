from datetime import datetime

from pydantic import BaseModel, ConfigDict, alias_generators, field_validator

from application.account.schemas.user_schemas import UserReadSchemaShort
from application.comment.schemas import CommentReadWithChildSchema
from application.community.models import CommunityThemes as CommunityTheme


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


class PostCreateSchema(BaseModel):
    model_config = ConfigDict(alias_generator=alias_generators.to_camel,
                              populate_by_name=True, from_attributes=True)

    title: str
    content: str | None = None
    author_id: int | None = None
    community_id: int | None = None

    @field_validator('community_id', mode='before')
    def community_id_before(cls, v):
        if v == 0:
            return None
        return v


class PostUpdateSchema(BaseModel):
    title: str | None = None
    content: str | None = None

