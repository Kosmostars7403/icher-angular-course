from datetime import datetime

from fastapi import Depends
from sqlalchemy import Column, String, Boolean, Integer, TIMESTAMP, Date, ARRAY, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy_file import ImageField

from application.account.schemas import UserInDBSchema
from database.db import Base, get_async_session, async_session


class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tg_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    name: Mapped[str | None] = mapped_column(String(length=200), nullable=False)
    last_name: Mapped[str | None] = mapped_column(String(length=200), nullable=False)
    username: Mapped[str] = mapped_column(String(length=320), unique=True, index=True, nullable=False)
    image: ImageField | None = Column(ImageField())
    stack: ARRAY | None = Column(ARRAY(String), default=[])
    city: Mapped[str | None] = mapped_column(String(length=100))
    description: Mapped[str | None] = mapped_column(String(length=1000))

    registered_at: Mapped[Date] = mapped_column(TIMESTAMP, default=datetime.utcnow)
    hashed_password: Mapped[str] = mapped_column(String(length=1024), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


async def get_user(username: str):
    async with async_session() as session:

        stmt = select(User).filter(User.username == username)
        user = await session.execute(stmt)
        user = user.scalar_one_or_none()

        if user:
            return UserInDBSchema.model_validate(user)
        else:
            return None
