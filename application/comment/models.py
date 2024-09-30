from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Integer, String, ForeignKey, TIMESTAMP, Date, BigInteger, BIGINT
from sqlalchemy.orm import relationship, mapped_column, Mapped

from application.account.models import User
from database.db import Base

if TYPE_CHECKING:
    from application.post.models import Post


class Comment(Base):
    __tablename__ = 'comment'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    text: Mapped[str] = mapped_column(String(255))
    author_id: Mapped[BigInteger] = mapped_column(BIGINT, ForeignKey('user.id'))
    post_id: Mapped[int] = mapped_column(Integer, ForeignKey('post.id'))
    comment_id: Mapped[int | None] = mapped_column(Integer, ForeignKey('comment.id'))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)
    updated_at: Mapped[datetime | None] = mapped_column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    post: Mapped['Post'] = relationship(back_populates='comments')
    author: Mapped['User'] = relationship(back_populates='comments')
    comments: Mapped[list['Comment']] = relationship(remote_side=[comment_id])
