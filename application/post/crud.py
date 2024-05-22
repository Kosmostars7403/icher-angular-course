import os

from sqlalchemy.ext.asyncio import AsyncSession

from application.account.models import User
from application.comment.models import Comment
from application.post.models import Post
from sqlalchemy import select, update, delete, insert
from sqlalchemy.orm import selectinload

from application.post.schemas import PostCreateSchema, PostUpdateSchema


async def get_post_by_id(post_id: int, session: AsyncSession):
    return await session.get(Post, post_id, options=[selectinload(Post.comments).options(selectinload(Comment.author)),
                                                                                         selectinload(Post.author)
                                                     ])


async def get_all_posts(session: AsyncSession):
    stmt = select(Post).options(
        selectinload(Post.comments).options(selectinload(Comment.author)),
        selectinload(Post.author),
    )
    return (await session.execute(stmt)).scalars().all()


async def get_posts_by_subscriptions(user: User, session: AsyncSession):
    stmt = select(Post).where(Post.author_id.in_(user.subscriptions)).options(
        selectinload(Post.comments).options(selectinload(Comment.author)),
        selectinload(Post.author)
    )
    return (await session.execute(stmt)).scalars().all()


async def create_post(post: PostCreateSchema, session: AsyncSession):
    stmt = insert(Post).values(**post.model_dump(exclude_none=True)).returning(Post.id)

    post_id = await session.scalar(stmt)
    await session.commit()

    return await get_post_by_id(post_id, session)


async def update_post(post_id: int, post: PostUpdateSchema, session: AsyncSession):
    stmt = update(Post).where(Post.id == post_id).values(**post.model_dump(exclude_none=True))
    await session.execute(stmt)
    await session.commit()


async def delete_post(post_id: int, session: AsyncSession):
    post = await get_post_by_id(post_id, session)
    stmt = delete(Post).where(Post.id == post_id)

    if os.path.exists(post.images):
        for image in post.images:
            os.remove(image)

    await session.execute(stmt)
    await session.commit()


async def upload_image_in_db_post(post_id: int, image_url: str, session: AsyncSession):
    post = await get_post_by_id(post_id, session)
    images = post.images

    if image_url not in images:
        images.append(image_url)
        stmt = update(Post).where(Post.id == post_id).values(images=images)
        await session.execute(stmt)
        await session.commit()
