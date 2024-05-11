from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, insert, delete

from application.message.models import Message


async def read_personal_chat_user_messages(chat_id: int, user_id: int, session: AsyncSession):
    stmt = update(Message).filter(Message.personal_chat_id == chat_id, Message.user_from_id != user_id).values(
        is_read=True)

    await session.execute(stmt)
    await session.commit()


async def insert_message(text: str, chat_id: int, user_id: int, session: AsyncSession):
    stmt = insert(Message).values(
        {
            'text': text,
            'user_from_id': user_id,
            'personal_chat_id': chat_id,
        }
    ).returning(Message.id)

    message_id = await session.scalar(stmt)
    await session.commit()

    return message_id


async def get_message(message_id: int, session: AsyncSession):
    stmt = select(Message).filter(Message.id == message_id)

    return await session.scalar(stmt)


async def update_message(message_id: int, text: str, session: AsyncSession):
    stmt = update(Message).filter(Message.id == message_id).values(text=text)
    await session.execute(stmt)
    await session.commit()


async def delete_message(message_id: int, session: AsyncSession):
    stmt = delete(Message).filter(Message.id == message_id)
    await session.execute(stmt)
    await session.commit()
