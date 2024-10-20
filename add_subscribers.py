import asyncio

from sqlalchemy import select, func
from sqlalchemy.dialects.postgresql.array import CONTAINS

from application.account.crud import get_user_by_id, update_user
from application.account.models import User
from database.db import async_session


async def add_subs():
    bots_ids = [123, 124, 125, 126, 127, 500]
    users_ids = []
    async with async_session() as session:
        stmt = select(User.id).filter(User.is_active)

        data = (await session.execute(stmt)).scalars().all()
        for user in data:
            user_id = user
            stmt = select(func.count()).where(CONTAINS(User.subscriptions, [user_id]))
            result = await session.execute(stmt)

            if result.first()[0] < 5:
                users_ids.append(user_id)

        if users_ids:
            for bot_id in bots_ids:
                bot = await get_user_by_id(bot_id, session)
                bot.subscriptions.extend(users_ids)
                await update_user(bot, {'subscriptions': bot.subscriptions}, session)


if __name__ == "__main__":
    asyncio.run(add_subs())
