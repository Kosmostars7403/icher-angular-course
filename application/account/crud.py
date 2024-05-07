from sqlalchemy import select, update, delete

from application.account.models import User
from database.db import async_session


async def get_user(username: str):
    async with async_session() as session:

        stmt = select(User).filter(User.username == username)
        user = await session.execute(stmt)
        user = user.scalar_one_or_none()

        return user


async def update_user(user: User, data: dict):
    async with async_session() as session:
        stmt = update(User).where(User.id == user.id).values(**data)
        await session.execute(stmt)
        await session.commit()

        return await get_user(user.username)


async def delete_user(user: User):
    async with async_session() as session:
        stmt = delete(User).where(User.id == user.id)
        await session.execute(stmt)
        await session.commit()
