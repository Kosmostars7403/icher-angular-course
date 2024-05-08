from pydantic import BaseModel,ConfigDict
from datetime import datetime
from typing import Optional

class PostBase(BaseModel):
    title: str
    content: str

class PostCreate(BaseModel):
    title: str
    content: str
    author: int

class Post(PostBase):
    id: int
    created_at: datetime
    author: int

    model_config = ConfigDict(from_attributes=True)
