from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, String, Boolean, Integer, TIMESTAMP, Date, ARRAY, BigInteger, BIGINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.db import Base

IMAGE_DIR = 'static/avatars'

if TYPE_CHECKING:
    from application.post.models import Post
    from application.comment.models import Comment


class User(Base):
    __tablename__ = 'user'

    id: Mapped[BigInteger] = mapped_column(BIGINT, unique=True, nullable=False, primary_key=True)
    first_name: Mapped[str | None] = mapped_column(String(length=200))
    last_name: Mapped[str | None] = mapped_column(String(length=200))
    username: Mapped[str] = mapped_column(String(length=320), unique=True, index=True, nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(length=1024))
    stack: ARRAY | None = Column(ARRAY(String), default=[])
    city: Mapped[str | None] = mapped_column(String(length=100))
    description: Mapped[str | None] = mapped_column(String(length=1000))
    subscriptions: ARRAY | None = Column(ARRAY(BIGINT), default=[])

    registered_at: Mapped[Date] = mapped_column(TIMESTAMP, default=datetime.utcnow)
    hashed_password: Mapped[str] = mapped_column(String(length=1024), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    posts: Mapped[list['Post']] = relationship(back_populates='author')
    comments: Mapped[list['Comment']] = relationship(back_populates='author')


