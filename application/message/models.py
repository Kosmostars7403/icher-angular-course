from sqlalchemy import Integer, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from database.db import Base


class Message(Base):
    __tablename__ = 'message'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_from: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'))
    user_to: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'))
    message: Mapped[str] = mapped_column(String)

