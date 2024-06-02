import os

from sqlalchemy import select, update, delete, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from application.account.filters import UserFilter
from application.account.models import User
from application.account.schemas.user_schemas import UserReadSchemaShort
from application.comment.models import Comment
from application.message.models import Message
from application.personal_chat.models import PersonalChat
from application.post.models import Post
from database.db import async_session


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


async def upload_image_in_db(user: User, avatar_url: str, session: AsyncSession):
    stmt = update(User).where(User.id == user.id).values(avatar_url=avatar_url)
    await session.execute(stmt)
    await session.commit()


async def delete_user(user: User, session: AsyncSession):
    stmt = delete(Message).where(Message.user_from_id == user.id)
    await session.execute(stmt)

    stmt = delete(Comment).where(Comment.author_id == user.id)
    await session.execute(stmt)

    stmt = delete(Post).where(Post.author_id == user.id)
    await session.execute(stmt)

    stmt = delete(PersonalChat).where(PersonalChat.user_first_id == user.id or PersonalChat.user_second_id == user.id)
    await session.execute(stmt)

    stmt = delete(User).where(User.id == user.id)

    if user.avatar_url is not None:
        if os.path.exists(user.avatar_url):
            os.remove(user.avatar_url)

    await session.execute(stmt)
    await session.commit()


async def delete_user_image(user: User, session: AsyncSession):
    stmt = update(User).where(User.id == user.id).values(avatar_url=None)

    if user.avatar_url is not None:
        if os.path.exists(user.avatar_url):
            os.remove(user.avatar_url)

    await session.execute(stmt)
    await session.commit()


async def get_all_users(user_filter: UserFilter, user: User, session: AsyncSession, stack: str, first_name: str,
                        last_name: str):
    stmt = select(User).filter(User.is_active and User.id != user.id)

    similarity_threshold = 0.3

    if stack:
        stack = stack.lower().split(',')

        subquery = select(
            User.id.label('user_id'),
            func.unnest(User.stack).label('unnested_stack')
        ).subquery()

        similarity_clauses = [
            func.similarity(subquery.c.unnested_stack, search_word) > similarity_threshold
            for search_word in stack
        ]
        similarity_filter = or_(*similarity_clauses)

        stmt = stmt.join(
            subquery,
            and_(
                User.id == subquery.c.user_id,
                similarity_filter
            )
        ).group_by(User.id)

    if first_name:
        stmt = stmt.filter(func.similarity(User.first_name, first_name) > similarity_threshold)

    if last_name:
        stmt = stmt.filter(func.similarity(User.last_name, last_name) > similarity_threshold)

    query_filter = user_filter.filter(user_filter.sort(stmt))

    filtered_data = [UserReadSchemaShort.model_validate(user) for user in
                     (await session.execute(query_filter)).scalars().all()]

    return filtered_data


async def get_test_users(session: AsyncSession):
    stmt = select(User).filter(User.is_active and User.id.in_([123, 124, 125, 126, 127])).order_by(User.id)
    return (await session.execute(stmt)).scalars().all()


async def get_user_by_id(user_id: int, session: AsyncSession):
    stmt = select(User).where(User.id == user_id)
    user = await session.scalar(stmt)

    return user


async def get_user_subscriptions(user: User, session: AsyncSession):

    user.subscriptions = [await get_user_by_id(user_id, session) for user_id in user.subscriptions]

    return user
