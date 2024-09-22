import json
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from application.account.crud import get_user_by_id
from application.account.helpers import get_current_active_user, get_current_token_payload, get_user_by_token_sub
from application.account.models import User
from application.account.validation import validate_token_type
from application.message.crud import read_personal_chat_user_messages
from application.personal_chat.crud import get_personal_chat, get_personal_chats_by_user, create_personal_chat_db
from application.personal_chat.schemas import PersonalChatReadSchema, PersonalChatReadShortSchema
from application.personal_chat.ws_manager import manager, ERROR_TOKEN
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

    if current_user.id in manager.user_connections.keys():
        await manager.send_unread_notify(current_user=current_user)

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
            message=(chat.messages[-1].text[:100] if len(chat.messages) > 0 else None),
            created_at=(chat.messages[-1].created_at if len(chat.messages) > 0 else None),
        ))

    return chats_schemas


@router.websocket("/ws/")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    user = None

    try:
        sec_websocket_protocol = websocket._headers['sec-websocket-protocol']
        payload = get_current_token_payload(sec_websocket_protocol)
        await validate_token_type(payload, 'access')
        user = await get_user_by_token_sub(payload)

    except Exception:
        await manager.send_personal_message(
            message=ERROR_TOKEN,
            websocket=websocket
        )

    if user is not None:
        await manager.add_user_connection(websocket, user.id)
        await manager.send_unread_notify(current_user=user)

    try:
        while True:
            data = await websocket.receive_text()
            data = json.loads(data)
            await manager.send_message_to_chat(data, websocket, user=user)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        if user is not None:
            manager.disconnect_user(user.id)
