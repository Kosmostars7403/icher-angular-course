from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, Integer, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.db import Base

if TYPE_CHECKING:
    from application.comment.models import Comment
    from application.account.models import User


class Post(Base):
    __tablename__ = 'post'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    author_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str | None] = mapped_column(String)
    created_at: Mapped[Date] = mapped_column(Date, default=datetime.utcnow)
    updated_at: Mapped[Date | None] = mapped_column(Date, default=datetime.utcnow, onupdate=datetime.utcnow)

    comments: Mapped[list['Comment']] = relationship(back_populates='post')
    author: Mapped['User'] = relationship(back_populates='posts')
