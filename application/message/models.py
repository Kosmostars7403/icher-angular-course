from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from database.db import Base


class Message(Base):
    __tablename__ = 'message'


