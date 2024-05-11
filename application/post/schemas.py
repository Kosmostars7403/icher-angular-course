from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict, alias_generators

from application.account.schemas.user_schemas import UserReadSchema, UserReadSchemaShort
from application.comment.schemas import CommentReadSchema


class PostReadSchema(BaseModel):
    model_config = ConfigDict(alias_generator=alias_generators.to_camel, populate_by_name=True,
                              from_attributes=True)

    id: int
    title: str
    content: str | None = ''
    author: UserReadSchemaShort
    created_at: datetime
    updated_at: datetime | None = None

    comments: list[CommentReadSchema] | None = []


class PostCreateSchema(BaseModel):
    model_config = ConfigDict(alias_generator=alias_generators.to_camel,
                              populate_by_name=True, from_attributes=True)

    title: str
    content: str | None = None
    author_id: int | None = None


class PostUpdateSchema(BaseModel):
    title: str | None = None
    content: str | None = None
