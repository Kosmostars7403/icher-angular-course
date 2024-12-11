import os

from sqlalchemy import select, update, delete, func, or_, and_, not_
from sqlalchemy.dialects.postgresql.array import CONTAINS
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

        if user:
            user = await get_user_by_id(user.id, session)

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

    stmt = delete(PersonalChat).where(or_(PersonalChat.user_first_id == user.id,PersonalChat.user_second_id == user.id))
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

    stmt = select(User).filter(User.is_active and User.id != user.id and User.username != 'test_user_ws')

    return await filter_accounts_by_tgrm(stmt, user_filter, session, stack, first_name, last_name)


async def get_subscribers(user_filter: UserFilter, user: User, session: AsyncSession, stack: str, first_last_name: str):
    stmt = select(User).filter(User.is_active).filter(CONTAINS(User.subscriptions, [user.id]))
    return await filter_subs_by_tgrm(stmt, user_filter, session, stack, first_last_name)


async def get_test_users(session: AsyncSession):
    stmt = select(User).filter(User.is_active and User.id.in_([123, 124, 125, 126, 127])).order_by(User.id)

    data = (await session.execute(stmt)).scalars().all()

    for user in data:
        stmt = select(func.count()).where(CONTAINS(User.subscriptions, [user.id]))
        result = await session.execute(stmt)

        user.subscribers_amount = result.first()[0]

    return data


async def get_user_by_id(user_id: int, session: AsyncSession):
    subquery = select(func.count()).where(CONTAINS(User.subscriptions, [user_id])).subquery(
        'subscribers_amount')

    stmt = select(User, subquery).where(User.id == user_id)

    result = await session.execute(stmt)

    result = result.first()

    if result is None:
        return None

    user, subscribers_amount = result

    user.subscribers_amount = subscribers_amount

    return user


async def get_user_subscriptions(user_filter: UserFilter, user: User, session: AsyncSession, stack: str,
                                 first_name: str,
                                 last_name: str):

    stmt = select(User).filter(User.is_active)

    filtered_data = await filter_accounts_by_tgrm(stmt, user_filter, session, stack, first_name, last_name)

    return [result_user for result_user in filtered_data if result_user.id in user.subscriptions]


async def filter_accounts_by_tgrm(stmt, user_filter: UserFilter, session: AsyncSession, stack: str, first_name: str,
                                  last_name: str):
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

    data = (await session.execute(query_filter)).scalars().all()

    for user in data:
        stmt = select(func.count()).where(CONTAINS(User.subscriptions, [user.id]))
        result = await session.execute(stmt)

        user.subscribers_amount = result.first()[0]

    filtered_data = [UserReadSchemaShort.model_validate(user) for user in
                     data]

    return filtered_data

async def filter_subs_by_tgrm(stmt, user_filter: UserFilter, session: AsyncSession, stack: str, first_last_name: str):
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

    if first_last_name:
        stmt = stmt.filter(or_(func.similarity(User.first_name, first_last_name) > similarity_threshold,
                               func.similarity(User.last_name, first_last_name) > similarity_threshold))

    query_filter = user_filter.filter(user_filter.sort(stmt))

    data = (await session.execute(query_filter)).scalars().all()

    for user in data:
        stmt = select(func.count()).where(CONTAINS(User.subscriptions, [user.id]))
        result = await session.execute(stmt)

        user.subscribers_amount = result.first()[0]

    filtered_data = [UserReadSchemaShort.model_validate(user) for user in
                     data]

    return filtered_data
