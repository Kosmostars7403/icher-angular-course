from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Integer, ForeignKey, String, ARRAY, Column, Enum as SQLEnum, BIGINT, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.db import Base

if TYPE_CHECKING:
    from application.post.models import Post
    from application.account.models import User


class CommunityThemes(Enum):
    PROGRAMMING = "PROGRAMMING"
    TECHNOLOGY = "TECHNOLOGY"
    EDUCATION = "EDUCATION"
    SPORT = "SPORT"
    OTHER = "OTHER"

class ImageType(Enum):
    BANNER = "BANNER"
    AVATAR = "AVATAR"


class Community(Base):
    __tablename__ = 'community'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    admin_id: Mapped[BigInteger] = mapped_column(BIGINT, ForeignKey('user.id'))
    name: Mapped[str] = mapped_column(String(length=128))
    themes: ARRAY | None = Column(ARRAY(SQLEnum(CommunityThemes)), default=[])
    tags: ARRAY = Column(ARRAY(String), default=[])
    banner_url: Mapped[str | None] = mapped_column(String(length=1024))
    avatar_url: Mapped[str | None] = mapped_column(String(length=1024))
    description: Mapped[str | None] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    subscribers: ARRAY | None = Column(ARRAY(BIGINT), default=[])

    posts: Mapped[list['Post']] = relationship(back_populates='community')
    admin: Mapped['User'] = relationship(back_populates='communities')
