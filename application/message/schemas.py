from datetime import datetime

from pydantic import BaseModel, ConfigDict, alias_generators


class MessageReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, alias_generator=alias_generators.to_camel, populate_by_name=True)

    id: int
    user_from_id: int
    personal_chat_id: int
    text: str
    created_at: datetime
    is_read: bool
    updated_at: datetime | None = None