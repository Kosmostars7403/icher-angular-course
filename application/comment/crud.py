from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, insert
from sqlalchemy.orm import selectinload

from application.comment.models import Comment
from application.comment.schemas import CommentUpdateSchema, CommentCreateSchema


async def get_comment_by_id(comment_id: int, session: AsyncSession):
    return await session.get(Comment, comment_id, options=[selectinload(Comment.author),selectinload(Comment.comments)])


async def update_comment(comment_id: int, comment: CommentUpdateSchema, session: AsyncSession):
    stmt = update(Comment).where(Comment.id == comment_id).values(**comment.model_dump(exclude_none=True))
    await session.execute(stmt)
    await session.commit()


async def delete_comment(comment_id: int, session: AsyncSession):

    stmt = update(Comment).where(Comment.comment_id == comment_id).values(comment_id=None)
    await session.execute(stmt)

    stmt = delete(Comment).where(Comment.id == comment_id)
    await session.execute(stmt)

    await session.commit()


async def create_comment(comment: CommentCreateSchema, session: AsyncSession):
    stmt = insert(Comment).values(**comment.model_dump(exclude_none=True)).returning(Comment.id)

    comment_id = await session.scalar(stmt)

    await session.commit()

    return await get_comment_by_id(comment_id, session)
