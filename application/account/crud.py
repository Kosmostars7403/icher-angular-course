import math

from sqlalchemy import select, update, delete

from application.account.filters import UserFilter
from application.account.models import User
from application.account.schemas.user_schemas import UserReadSchemaShort
from database.db import async_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql.array import CONTAINS
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


async def upload_image_in_db(user: User, avatar_url: str, session: AsyncSession):
    stmt = update(User).where(User.id == user.id).values(avatar_url=avatar_url)
    await session.execute(stmt)
    await session.commit()

    return await get_user(user.username)


async def delete_user(user: User, session: AsyncSession):

    stmt = delete(User).where(User.id == user.id)

    if os.path.exists(user.avatar_url):
        os.remove(user.avatar_url)

    await session.execute(stmt)
    await session.commit()


async def get_all_users(user_filter: UserFilter, user: User, session: AsyncSession, stack: str):

    if stack:
        stack = stack.split(',')
        stmt = select(User).where(User.is_active and User.id != user.id and CONTAINS(User.stack, stack))
    else:
        stmt = select(User).where(User.is_active and User.id != user.id)

    query_filter = user_filter.filter(user_filter.sort(stmt))

    filtered_data = [UserReadSchemaShort.model_validate(user) for user in
                     (await session.execute(query_filter)).scalars()]

    return filtered_data
