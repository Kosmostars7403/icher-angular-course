from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from application.account.crud import get_user_by_id
from application.account.helpers import get_current_active_user
from application.account.models import User
from application.message.crud import read_personal_chat_user_messages
from application.personal_chat.crud import get_personal_chat, get_personal_chats_by_user, create_personal_chat_db
from application.personal_chat.schemas import PersonalChatReadSchema, PersonalChatReadShortSchema
from database.db import get_async_session

router = APIRouter(
    tags=['chat'],
    prefix='/chat'
)


@router.post('/{user_id}', response_model=PersonalChatReadSchema)
async def create_personal_chat(user_id: int, current_user: Annotated[User, Depends(get_current_active_user)],
                               session: AsyncSession = Depends(get_async_session)):

    if await get_user_by_id(user_id=user_id, session=session) is None:
        raise HTTPException(status_code=404, detail='User not found')

    chat_id = await create_personal_chat_db(user_id=user_id, current_user_id=current_user.id, session=session)

    return await get_personal_chat(chat_id=chat_id, session=session)


@router.get('/{chat_id}', response_model=PersonalChatReadSchema)
async def read_personal_chat(chat_id: int, current_user: Annotated[User, Depends(get_current_active_user)],
                             session: AsyncSession = Depends(get_async_session)):
    await read_personal_chat_user_messages(chat_id=chat_id, user_id=current_user.id, session=session)

    personal_chat = await get_personal_chat(chat_id=chat_id, session=session)

    if personal_chat is None:
        raise HTTPException(status_code=404, detail='Chat not found')

    return personal_chat


@router.get('/get_my_chats/', response_model=list[PersonalChatReadShortSchema])
async def get_chats(current_user: Annotated[User, Depends(get_current_active_user)],
                    session: AsyncSession = Depends(get_async_session)):
    chats = await get_personal_chats_by_user(user=current_user, session=session)

    chats_schemas = []

    for chat in chats:
        chats_schemas.append(PersonalChatReadShortSchema(
            id=chat.id,
            user_from=chat.user_first if chat.user_first_id != current_user.id else chat.user_second,
            message=(chat.messages[-1].text[:100] if len(chat.messages) > 0 else None)
        ))

    return chats_schemas
