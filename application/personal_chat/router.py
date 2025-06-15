import json
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
# from fastapi.responses import HTMLResponse
from fastapi_limiter.depends import RateLimiter, WebSocketRateLimiter
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
from settings import settings

LIMITER_DEPENDS = Depends(RateLimiter(times=settings.LIMIT_TIMES, seconds=settings.LIMIT_SEC))

router = APIRouter(
    tags=['chat'],
    prefix='/chat'
)

@router.post('/{user_id}', response_model=PersonalChatReadSchema, dependencies=[LIMITER_DEPENDS])
async def create_personal_chat(user_id: int, current_user: Annotated[User, Depends(get_current_active_user)],
                               session: AsyncSession = Depends(get_async_session)):

    if await get_user_by_id(user_id=user_id, session=session) is None:
        raise HTTPException(status_code=404, detail='User not found')

    chat_id = await create_personal_chat_db(user_id=user_id, current_user_id=current_user.id, session=session)

    return await get_personal_chat(chat_id=chat_id, session=session)


@router.get('/{chat_id}', response_model=PersonalChatReadSchema, dependencies=[LIMITER_DEPENDS])
async def read_personal_chat(chat_id: int, current_user: Annotated[User, Depends(get_current_active_user)],
                             session: AsyncSession = Depends(get_async_session)):
    await read_personal_chat_user_messages(chat_id=chat_id, user_id=current_user.id, session=session)

    personal_chat = await get_personal_chat(chat_id=chat_id, session=session)

    if personal_chat is None:
        raise HTTPException(status_code=404, detail='Chat not found')

    if current_user.id != personal_chat.user_second_id and current_user.id != personal_chat.user_first_id:
        raise HTTPException(status_code=403, detail="It's not your chat")

    if current_user.id in manager.user_connections.keys():
        await manager.send_unread_notify(current_user=current_user)

    return personal_chat


@router.get('/get_my_chats/', response_model=list[PersonalChatReadShortSchema], dependencies=[LIMITER_DEPENDS])
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
            unread_messages=chat.unread_messages
        ))

    return chats_schemas

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    ratelimit = WebSocketRateLimiter(times=8, seconds=settings.LIMIT_SEC)

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
        await websocket.close(reason='Invalid token')
        manager.disconnect(websocket)
        return

    try:
        if user:
            await manager.add_user_connection(websocket, user.id)
            await manager.send_unread_notify(current_user=user)

        while True:

            data = await websocket.receive_text()
            try:
                data = json.loads(data)
                await ratelimit(websocket, context_key=data)

                if not isinstance(data, dict):
                    await manager.send_personal_message(
                        message=json.dumps({'status': 'error', 'message': 'Invalid message'}),
                        websocket=websocket
                    )
                    continue

                if 'text' not in data.keys() and 'chat_id' not in data.keys():
                    await manager.send_personal_message(
                        message=json.dumps({'status': 'error', 'message': 'Invalid message'}),
                        websocket=websocket
                    )
                else:
                    await manager.send_message_to_chat(data, websocket, user=user)

            except HTTPException:
                await manager.send_personal_message(
                    message=json.dumps({'status': 'error', 'message': 'Too many messages'}),
                    websocket=websocket
                )

            except Exception:
                await manager.send_personal_message(
                    message=json.dumps({'status': 'error', 'message': 'Invalid message'}),
                    websocket=websocket
                )

    except WebSocketDisconnect:
        print(f"WebSocket disconnected for user {user.id if user else 'unknown'}")
    except Exception as e:
        print(f'Error with websocket: {e}')
    finally:
        manager.disconnect(websocket)
        if user:
            manager.disconnect_user(user.id)

# html = '''<!DOCTYPE html>
# <html>
#     <head>
#         <title>WebSocket Example</title>
#     </head>
#     <body>
#         <h1>WebSocket Example</h1>
#         <div>
#             <label for="token-input">Token:</label>
#             <input type="text" id="token-input" style="width: 300px;"
#                    value="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0eXBlIjoiYWNjZXNzIiwic3ViIjoiZ2lkZHlPYXRtZWFsMyIsImV4cCI6MTc0OTk5OTY1NX0.YLBmdEbUsIIZrb40hEPAQswSuJW1QkIObSi3cttoK3Q">
#         </div>
#         <div>
#             <label for="message-input">Message:</label>
#             <input type="text" id="message-input" value='{"text": "Hello from server", "chat_id": 9}'>
#         </div>
#         <button onclick="connectWebSocket()">Connect</button>
#         <button onclick="sendMessage()" id="send-btn" disabled>Send Message</button>
#
#         <script>
#             let ws = null;
#
#             function connectWebSocket() {
#                 const token = document.getElementById('token-input').value;
#                 if (!token) {
#                     alert("Please enter a token");
#                     return;
#                 }
#
#                 ws = new WebSocket("ws://localhost:8000/chat/ws", [token]);
#
#                 ws.onmessage = function(event) {
#                     const message = event.data;
#                     alert("Message from server: " + message);
#                 };
#
#                 ws.onopen = function() {
#                     alert("WebSocket connection established");
#                     document.getElementById('send-btn').disabled = false;
#                 };
#
#                 ws.onclose = function() {
#                     alert("WebSocket connection closed");
#                     document.getElementById('send-btn').disabled = true;
#                 };
#
#                 ws.onerror = function(error) {
#                     alert("WebSocket error: " + error);
#                 };
#             }
#
#             function sendMessage() {
#                 if (!ws || ws.readyState !== WebSocket.OPEN) {
#                     alert("WebSocket is not connected");
#                     return;
#                 }
#
#                 const message = document.getElementById('message-input').value;
#                 if (!message) {
#                     alert("Please enter a message");
#                     return;
#                 }
#
#                 try {
#                     ws.send(message);
#                 } catch (error) {
#                     alert("Error sending message: " + error);
#                 }
#             }
#         </script>
#     </body>
# </html>
# '''
#
# @router.get("/chat/test", response_class=HTMLResponse)
# async def get():
#     return html