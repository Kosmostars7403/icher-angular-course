from application.account.models import User
from application.account.schemas import UserInDBSchema
from database.db import async_session
from sqlalchemy import select


async def get_user(username: str):
    async with async_session() as session:

        stmt = select(User).filter(User.username == username)
        user = await session.execute(stmt)
        user = user.scalar_one_or_none()

        if user:
            return UserInDBSchema.model_validate(user)
        else:
            return None
