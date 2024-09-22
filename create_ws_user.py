import asyncio

from sqlalchemy import select

from application.account.models import User
from application.account.validation import get_password_hash
from database.db import async_session


async def create_ws_user():
    stmt = select(User).filter(User.username == "test_user_ws")

    async with async_session() as session:
        result = await session.execute(stmt)
        user = result.scalar()

        if not user:
            hashed_password = get_password_hash("websocket")
            new_ws_user = User(
                id=500,
                username="test_user_ws",
                first_name="Test",
                last_name="Websocket",
                avatar_url=None,
                stack=[],
                city=None,
                description=None,
                subscriptions=[],
                hashed_password=hashed_password,
                is_active=True,

            )
            session.add(new_ws_user)

            await session.commit()


if __name__ == "__main__":
    asyncio.run(create_ws_user())
