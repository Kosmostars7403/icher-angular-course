from datetime import datetime

from sqlalchemy import String, Integer, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from database.db import Base


class Post(Base):
    __tablename__ = 'post'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    author: Mapped[int] = mapped_column(ForeignKey('user.id'))
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[Date] = mapped_column(Date, default=datetime.utcnow)

