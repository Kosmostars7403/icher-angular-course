from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
# from sqlalchemy import select
from .models import Post


async def get_all_posts(session: AsyncSession):
    async with session.begin():
        result = await session.execute(select(Post))
        return result.scalars().all()
    

async def get_post(session: AsyncSession, post_id: int):
    return await session.get(Post, post_id)


async def create_post(session: AsyncSession, title: str, content: str, author: int):
    new_post = Post(
        title=title,
        content=content,
        author=author,
        created_at=datetime.utcnow()
    )
    session.add(new_post)
    await session.commit()
    return new_post



