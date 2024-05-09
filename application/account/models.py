from datetime import datetime
from sqlalchemy import Column, String, Boolean, Integer, TIMESTAMP, Date, ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from database.db import Base

IMAGE_DIR = 'static/avatars'


class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, primary_key=True)
    first_name: Mapped[str | None] = mapped_column(String(length=200))
    last_name: Mapped[str | None] = mapped_column(String(length=200))
    username: Mapped[str] = mapped_column(String(length=320), unique=True, index=True, nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(length=1024))
    stack: ARRAY | None = Column(ARRAY(String), default=[])
    city: Mapped[str | None] = mapped_column(String(length=100))
    description: Mapped[str | None] = mapped_column(String(length=1000))
    subscriptions: ARRAY | None = Column(ARRAY(Integer), default=[])

    registered_at: Mapped[Date] = mapped_column(TIMESTAMP, default=datetime.utcnow)
    hashed_password: Mapped[str] = mapped_column(String(length=1024), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)



