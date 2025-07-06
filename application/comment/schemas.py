from datetime import datetime

from pydantic import BaseModel, alias_generators, ConfigDict, field_validator

from application.account.schemas.user_schemas import UserReadSchemaShort


class CommentReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, alias_generator=alias_generators.to_camel,
                              populate_by_name=True)

    id: int
    text: str
    author: UserReadSchemaShort
    post_id: int
    comment_id: int | None = None
    created_at: datetime
    updated_at: datetime | None = None


class CommentReadWithChildSchema(CommentReadSchema):
    comments: list[CommentReadSchema]



class CommentCreateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, alias_generator=alias_generators.to_camel,
                              populate_by_name=True)
    text: str
    author_id: int | None = None
    post_id: int
    comment_id: int | None = None

    @field_validator('comment_id', mode='before')
    def comment_id_before(cls, v):
        if v == 0:
            return None
        return v


class CommentUpdateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, alias_generator=alias_generators.to_camel,
                              populate_by_name=True)
    text: str | None = None
