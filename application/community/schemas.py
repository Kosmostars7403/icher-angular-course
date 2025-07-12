from datetime import datetime
from typing import Optional, List, Any

from pydantic import BaseModel, ConfigDict, alias_generators, model_validator, field_validator

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
    is_joined: bool = False

class PostReadSchema(BaseModel):
    model_config = ConfigDict(alias_generator=alias_generators.to_camel, populate_by_name=True,
                              from_attributes=True)

    id: int
    title: str
    community_id: int | None = None
    content: str | None = ''
    author: UserReadSchemaShort | CommunityShortReadSchema = None
    images: list[str] | None = None
    created_at: datetime
    updated_at: datetime | None = None
    likes: int = 0
    likes_users: Optional[List] = None

    @model_validator(mode='before')
    @classmethod
    def transform_likes(cls, data: Any) -> Any:
        if isinstance(data, dict):
            return data

        if hasattr(data, 'likes'):
            likes_list = data.likes
            likes_users = [like.user_id for like in likes_list]

            # Создаем словарь с данными
            result = {
                **data.__dict__,
                'likes': len(likes_list),
                'likes_users': likes_users
            }
            return result

        return data

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
