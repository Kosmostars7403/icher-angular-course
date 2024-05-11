from typing import Annotated

from fastapi import APIRouter, status, Depends, HTTPException

from application.account.helpers import get_current_active_user
from application.account.models import User
from application.post.schemas import PostReadSchema, PostCreateSchema, PostUpdateSchema
from .crud import get_all_posts, create_post as crud_create_post, update_post as crud_update_post, \
    delete_post as crud_delete_post, get_post_by_id, get_posts_by_subscriptions
from sqlalchemy.ext.asyncio import AsyncSession

from database.db import get_async_session

router = APIRouter(
    tags=['post'],
    prefix='/post'
)


@router.get('/', status_code=status.HTTP_200_OK, response_model=list[PostReadSchema],
            dependencies=[Depends(get_current_active_user)])
async def get_posts(session: AsyncSession = Depends(get_async_session)):
    return await get_all_posts(session=session)


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=PostReadSchema)
async def create_post(post: PostCreateSchema, user: Annotated[User, Depends(get_current_active_user)],
                      session: AsyncSession = Depends(get_async_session)):
    post.author_id = user.id
    return await crud_create_post(post=post, session=session)


@router.get('/my_subscriptions', status_code=status.HTTP_200_OK, response_model=list[PostReadSchema])
async def get_my_subscriptions_post(user: Annotated[User, Depends(get_current_active_user)],
                                    session: AsyncSession = Depends(get_async_session)):

    return await get_posts_by_subscriptions(user=user, session=session)


@router.get('/{post_id}', status_code=status.HTTP_200_OK, response_model=PostReadSchema,
            dependencies=[Depends(get_current_active_user)])
async def get_post(post_id: int, session: AsyncSession = Depends(get_async_session)):
    post = await get_post_by_id(post_id=post_id, session=session)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post not found')
    return post


@router.patch('/{post_id}', status_code=status.HTTP_202_ACCEPTED, response_model=PostReadSchema)
async def update_post(post_id: int, post: PostUpdateSchema, user: Annotated[User, Depends(get_current_active_user)],
                      session: AsyncSession = Depends(get_async_session)):
    old_post = await get_post_by_id(post_id=post_id, session=session)

    if old_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post not found')

    if old_post.author_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='This is not your post')

    await crud_update_post(post_id=post_id, post=post, session=session)

    return await get_post_by_id(post_id=post_id, session=session)


@router.delete('/{post_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, user: Annotated[User, Depends(get_current_active_user)],
                      session: AsyncSession = Depends(get_async_session)):
    old_post = await get_post_by_id(post_id=post_id, session=session)

    if old_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post not found')

    if old_post.author_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='This is not your post')

    await crud_delete_post(post_id=post_id, session=session)
