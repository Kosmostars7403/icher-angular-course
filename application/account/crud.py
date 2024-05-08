from sqlalchemy import select, update, delete

from application.account.models import User
from database.db import async_session
from sqlalchemy.ext.asyncio import AsyncSession
import os


async def get_user(username: str):
    async with async_session() as session:
        stmt = select(User).filter(User.username == username)
        user = await session.execute(stmt)
        user = user.scalar_one_or_none()

        return user


async def update_user(user: User, data: dict, session: AsyncSession):

    stmt = update(User).where(User.id == user.id).values(**data)
    await session.execute(stmt)
    await session.commit()

    return await get_user(user.username)


async def upload_image_in_db(user: User, image_url: str, session: AsyncSession):
    stmt = update(User).where(User.id == user.id).values(image_url=image_url)
    await session.execute(stmt)
    await session.commit()

    return await get_user(user.username)


async def delete_user(user: User, session: AsyncSession):

    stmt = delete(User).where(User.id == user.id)

    if os.path.exists(user.image_url):
        os.remove(user.image_url)

    await session.execute(stmt)
    await session.commit()
