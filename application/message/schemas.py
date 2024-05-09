from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MessageReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_from_id: int
    personal_chat_id: int
    text: str
    created_at: datetime
    is_read: bool
    updated_at: datetime | None = None