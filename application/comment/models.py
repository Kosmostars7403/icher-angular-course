from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Integer, String, ForeignKey, TIMESTAMP, Date
from sqlalchemy.orm import relationship, mapped_column, Mapped

from application.account.models import User
from database.db import Base

if TYPE_CHECKING:
    from application.post.models import Post


class Comment(Base):
    __tablename__ = 'comment'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    text: Mapped[str] = mapped_column(String(255))
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'))
    post_id: Mapped[int] = mapped_column(Integer, ForeignKey('post.id'))
    comment_id: Mapped[int | None] = mapped_column(Integer, ForeignKey('comment.id'))
    created_at: Mapped[Date] = mapped_column(TIMESTAMP, default=datetime.utcnow)
    updated_at: Mapped[Date | None] = mapped_column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    post: Mapped['Post'] = relationship(back_populates='comments')
    author: Mapped['User'] = relationship(back_populates='comments')
