import json
from datetime import datetime

from fastapi import WebSocket

from application.account.crud import get_user_by_id
from application.account.models import User
from application.message.crud import insert_message
from application.message.validators import is_not_my_chat
from application.personal_chat.crud import get_unread_messages_count, get_personal_chat
from database.db import async_session

ERROR_TOKEN = json.dumps({
        'status': 'error',
        'message': 'Invalid token'}
)

ERROR_CHAT_NOT_FOUND = json.dumps({
    'status': 'error',
    'message': 'Chat not found'}
)

ERROR_CHAT_NOT_MY_CHAT = json.dumps({
    'status': 'error',
    'message': 'This is not your chat'})


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.user_connections: dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept(subprotocol=websocket._headers['sec-websocket-protocol'])
        self.active_connections.append(websocket)

    async def add_user_connection(self, websocket: WebSocket, user_id: int):
        self.user_connections[user_id] = websocket

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    def disconnect_user(self, user_id: int):
        self.user_connections.pop(user_id)

    @staticmethod
    async def send_personal_message(message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def send_message_to_chat(self, message: dict, websocket: WebSocket, user: User = None):
        if user is None:
            await self.send_personal_message(
                message=ERROR_TOKEN, websocket=websocket)
            return

        async with async_session() as session:
            personal_chat = await get_personal_chat(chat_id=message['chat_id'], session=session)

            if personal_chat is None:
                await self.send_personal_message(message=ERROR_CHAT_NOT_FOUND, websocket=websocket)
                return

            if await is_not_my_chat(chat=personal_chat, user_id=user.id):
                await self.send_personal_message(message=ERROR_CHAT_NOT_MY_CHAT, websocket=websocket)
                return

        message_id = await self.save_message_in_db(message['text'], message['chat_id'], user)

        message_json = json.dumps({
            'status': 'success',
            'action': 'message',
            'data': {
                'id': message_id,
                'message': message['text'],
                'chat_id': message['chat_id'],
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'author': user.id
            }
        }
        )

        await self.send_personal_message(
            message=message_json, websocket=websocket)

        getter_user_id = personal_chat.user_first_id if personal_chat.user_first_id != user.id else personal_chat.user_second_id

        await self.broadcast(message=message_json,
                             getter_user_id=getter_user_id)

    async def send_unread_notify(self, current_user: User):
        async with async_session() as session:
            await manager.send_personal_message(
                json.dumps({
                    'status': 'success',
                    'action': 'unread',
                    'data': {
                        'count': await get_unread_messages_count(current_user, session=session)
                    }
                }),
                websocket=self.user_connections[current_user.id]
            )

    @staticmethod
    async def save_message_in_db(message: str, chat_id: int, user: User):
        async with async_session() as session:
            return await insert_message(chat_id=chat_id, text=message, user_id=user.id, session=session)

    async def broadcast(self, message: str, getter_user_id: int):
        if getter_user_id in self.user_connections.keys():
            await self.user_connections[getter_user_id].send_text(message)
            async with async_session() as session:
                user = await get_user_by_id(getter_user_id, session=session)
                await self.send_unread_notify(user)


manager = ConnectionManager()
