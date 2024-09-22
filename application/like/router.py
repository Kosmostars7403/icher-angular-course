from typing import Annotated

from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from application.account.helpers import get_current_active_user
from application.account.models import User
from application.like.crud import create_like as create_like_db, delete_like as delete_like_db, \
    get_like_by_user_and_post_id
from application.like.schemas import LikeCreateSchema
from database.db import get_async_session

router = APIRouter(
    tags=['post'],
    prefix='/post/like'
)


@router.post('/{post_id}', status_code=status.HTTP_201_CREATED)
async def create_like(post_id: int, user: Annotated[User, Depends(get_current_active_user)],
                      session: AsyncSession = Depends(get_async_session)):
    like = await get_like_by_user_and_post_id(user_id=user.id, post_id=post_id, session=session)

    if like is None:
        await create_like_db(like=LikeCreateSchema(user_id=user.id,
                                                   post_id=post_id),
                             session=session)

        return {'message': 'Like created'}

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Like is already created")




@router.delete('/{post_id}', status_code=status.HTTP_202_ACCEPTED)
async def delete_like(post_id: int, user: Annotated[User, Depends(get_current_active_user)],
                      session: AsyncSession = Depends(get_async_session)):

    like = await get_like_by_user_and_post_id(user_id=user.id, post_id=post_id, session=session)

    if like is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Like not found!")

    await delete_like_db(like_id=like.id, session=session)

    return {'message': 'Like deleted'}
