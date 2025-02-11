from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from application.account.helpers import get_current_active_user
from application.account.models import User
from application.comment.schemas import CommentReadSchema, CommentUpdateSchema, CommentCreateSchema, CommentReadWithChildSchema
from database.db import get_async_session
from .crud import (get_comment_by_id, update_comment as crud_update_comment, delete_comment as crud_delete_comment,
                   create_comment as crud_create_comment)

from fastapi_limiter.depends import RateLimiter

from settings import settings

LIMITER_DEPENDS = Depends(RateLimiter(times=settings.LIMIT_TIMES, seconds=settings.LIMIT_SEC))

router = APIRouter(
    tags=['comment'],
    prefix='/comment',
)


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=CommentReadSchema, dependencies=[LIMITER_DEPENDS])
async def create_comment(comment: CommentCreateSchema, user: Annotated[User, Depends(get_current_active_user)],
                         session: AsyncSession = Depends(get_async_session)):
    comment.author_id = user.id
    return await crud_create_comment(comment=comment, session=session)


@router.get('/{comment_id}', status_code=status.HTTP_200_OK, response_model=CommentReadWithChildSchema,
            dependencies=[Depends(get_current_active_user), LIMITER_DEPENDS])
async def get_comment(comment_id: int, session: AsyncSession = Depends(get_async_session)):

    comment = await get_comment_by_id(comment_id=comment_id, session=session)

    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Comment not found')

    return comment


@router.patch('/{comment_id}', status_code=status.HTTP_202_ACCEPTED, dependencies=[LIMITER_DEPENDS])
async def update_comment(comment_id: int, comment: CommentUpdateSchema,
                         user: Annotated[User, Depends(get_current_active_user)],
                         session: AsyncSession = Depends(get_async_session)):
    old_comment = await get_comment_by_id(comment_id=comment_id, session=session)

    if old_comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Comment not found')

    if old_comment.author_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='This is not your comment')

    await crud_update_comment(comment_id=comment_id, comment=comment, session=session)

    return await get_comment_by_id(comment_id=comment_id, session=session)


@router.delete('/{comment_id}', status_code=status.HTTP_204_NO_CONTENT,dependencies=[LIMITER_DEPENDS])
async def delete_comment(comment_id: int, user: Annotated[User, Depends(get_current_active_user)],
                         session: AsyncSession = Depends(get_async_session)):
    old_comment = await get_comment_by_id(comment_id=comment_id, session=session)

    if old_comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Comment not found')

    if old_comment.author_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='This is not your comment')

    await crud_delete_comment(comment_id=comment_id, session=session)

