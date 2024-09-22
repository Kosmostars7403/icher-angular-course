from sqlalchemy import select, insert, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from application.account.models import User
from application.personal_chat.models import PersonalChat


async def check_if_chat_exists(user_id: int, current_user_id: int, session: AsyncSession):
    stmt = select(PersonalChat.id).filter(
        or_((PersonalChat.user_first_id == user_id and PersonalChat.user_second_id == current_user_id),
            PersonalChat.user_second_id == user_id and PersonalChat.user_first_id == current_user_id))

    if chat_id := await session.scalar(stmt):
        return chat_id

    return None


async def get_personal_chat(chat_id: int, session: AsyncSession):
    stmt = select(PersonalChat).where(PersonalChat.id == chat_id).options(
        selectinload(PersonalChat.messages),
        selectinload(PersonalChat.user_first),
        selectinload(PersonalChat.user_second),
    )

    return (await session.execute(stmt)).scalar_one_or_none()


async def get_personal_chats_by_user(user: User, session: AsyncSession):
    stmt = select(PersonalChat).filter(
        or_(PersonalChat.user_first_id == user.id, PersonalChat.user_second_id == user.id)
        ).options(
        selectinload(PersonalChat.messages),
        selectinload(PersonalChat.user_first),
        selectinload(PersonalChat.user_second),
    )

    chats = (await session.execute(stmt)).scalars().all()

    return chats


async def get_unread_messages_count(user: User, session: AsyncSession):
    stmt = select(PersonalChat).filter(
        or_(PersonalChat.user_first_id == user.id, PersonalChat.user_second_id == user.id)
        ).options(
        selectinload(PersonalChat.messages),
    )

    chats = (await session.execute(stmt)).scalars().all()

    count_unread = 0
    for chat in chats:
        for message in chat.messages:
            if not message.is_read and message.user_from_id != user.id:
                count_unread += 1

    return count_unread

async def create_personal_chat_db(user_id: int, current_user_id: int, session: AsyncSession):

    if chat_id := await check_if_chat_exists(user_id, current_user_id, session):
        return chat_id

    stmt = insert(PersonalChat).values({
        'user_first_id': user_id,
        'user_second_id': current_user_id,
    }).returning(PersonalChat.id)

    chat_id = (await session.execute(stmt)).scalar()
    await session.commit()

    return chat_id
