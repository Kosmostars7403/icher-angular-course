from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, Integer, ForeignKey, ARRAY, Column, BigInteger, BIGINT
from sqlalchemy.orm import Mapped, mapped_column, relationship
from application.like.models import Like

from database.db import Base

if TYPE_CHECKING:
    from application.comment.models import Comment
    from application.account.models import User
    from application.community.models import Community


class Post(Base):
    __tablename__ = 'post'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    author_id: Mapped[BigInteger] = mapped_column(BIGINT, ForeignKey('user.id'))
    community_id: Mapped[int | None] = mapped_column(ForeignKey('community.id'))
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str | None] = mapped_column(String)
    images: ARRAY | None = Column(ARRAY(String), default=[])
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime | None] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    comments: Mapped[list['Comment']] = relationship(back_populates='post')
    author: Mapped['User'] = relationship(back_populates='posts')
    community: Mapped['Community'] = relationship(back_populates='posts')
    likes: Mapped[list['Like']] = relationship(back_populates='post')
