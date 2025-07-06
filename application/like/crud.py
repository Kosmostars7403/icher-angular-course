from sqlalchemy import insert, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from application.like.models import Like
from application.like.schemas import LikeCreateSchema

async def get_like_by_user_and_post_id(user_id: int, post_id: int, session: AsyncSession):
    stmt = select(Like).filter(Like.user_id == user_id, Like.post_id == post_id)
    result = await session.execute(stmt)
    result = result.scalar()
    return result if result else None

async def create_like(like: LikeCreateSchema, session: AsyncSession):
    stmt = insert(Like).values(**like.model_dump(exclude_none=True))

    await session.execute(stmt)
    await session.commit()

async def delete_like(like_id: int, session: AsyncSession):
    stmt = delete(Like).where(Like.id == like_id)
    await session.execute(stmt)
    await session.commit()