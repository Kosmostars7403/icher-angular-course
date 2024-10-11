from datetime import datetime

from pydantic import BaseModel, ConfigDict, alias_generators

from application.account.schemas.user_schemas import UserReadSchemaShort
from application.message.schemas import MessageReadSchema


class PersonalChatReadShortSchema(BaseModel):
    model_config = ConfigDict(alias_generator=alias_generators.to_camel, populate_by_name=True, from_attributes=True)

    id: int
    user_from: UserReadSchemaShort
    message: str | None = None
    created_at: datetime | None = None
    unread_messages: int = 0


class PersonalChatReadSchema(BaseModel):
    model_config = ConfigDict(alias_generator=alias_generators.to_camel, populate_by_name=True, from_attributes=True)

    id: int
    user_first: UserReadSchemaShort
    user_second: UserReadSchemaShort
    messages: list[MessageReadSchema] | None = []
