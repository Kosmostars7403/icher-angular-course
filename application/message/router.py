from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from application.account.helpers import get_current_active_user
from application.account.models import User
from application.message.crud import insert_message, get_message, update_message, delete_message
from sqlalchemy.ext.asyncio import AsyncSession

from application.message.schemas import MessageReadSchema
from database.db import get_async_session

router = APIRouter(
    tags=['message'],
    prefix='/message',

)


@router.post('/send/{chat_id}', response_model=MessageReadSchema, status_code=status.HTTP_201_CREATED)
async def send_message(chat_id: int, message: str, current_user: Annotated[User, Depends(get_current_active_user)],
                       session: AsyncSession = Depends(get_async_session)):
    message_id = await insert_message(chat_id=chat_id, text=message, user_id=current_user.id, session=session)

    return await get_message(message_id=message_id, session=session)


@router.get('/{message_id}', response_model=MessageReadSchema, dependencies=[Depends(get_current_active_user)],
            status_code=status.HTTP_200_OK)
async def get_my_message(message_id: int, session: AsyncSession = Depends(get_async_session)):
    if message := await get_message(message_id=message_id, session=session):
        return message

    else:
        raise HTTPException(status_code=404, detail='Message not found')


@router.patch('/{message_id}', response_model=MessageReadSchema, status_code=status.HTTP_202_ACCEPTED)
async def patch_my_message(message_id: int, text: str, current_user: Annotated[User, Depends(get_current_active_user)],
                           session: AsyncSession = Depends(get_async_session)):
    if (await get_message(message_id=message_id, session=session)).user_from_id != current_user.id:
        raise HTTPException(status_code=403, detail="This is not your message")

    await update_message(message_id=message_id, text=text, session=session)

    return await get_message(message_id=message_id, session=session)


@router.delete('/{message_id}',  status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_message(message_id: int, current_user: Annotated[User, Depends(get_current_active_user)],
                            session: AsyncSession = Depends(get_async_session)):
    if (await get_message(message_id=message_id, session=session)).user_from_id != current_user.id:
        raise HTTPException(status_code=403, detail="This is not your message")

    await delete_message(message_id=message_id, session=session)

