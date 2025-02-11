import os
from typing import Annotated

from fastapi import APIRouter, status, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from application.account.helpers import get_current_active_user
from application.account.models import User
from application.community.crud import get_community_by_id
from application.community.validators import validate_community_admin
from application.post.schemas import PostReadSchema, PostCreateSchema, PostUpdateSchema, CommunityShortReadSchema
from database.db import get_async_session
from application.post.crud import get_all_posts, create_post as crud_create_post, update_post as crud_update_post, \
    delete_post as crud_delete_post, get_post_by_id, get_posts_by_subscriptions, upload_image_in_db_post, \
    delete_image_from_post

from fastapi_limiter.depends import RateLimiter
from settings import settings

LIMITER_DEPENDS = Depends(RateLimiter(times=settings.LIMIT_TIMES, seconds=settings.LIMIT_SEC))

router = APIRouter(
    tags=['post'],
    prefix='/post'
)

IMAGE_POST_DIR = 'static/posts'

IMAGE_EXTENSIONS = [
    'bmp', 'gif', 'ico', 'ief', 'jpe', 'jpeg', 'jpg',
    'pbm', 'pgm', 'png', 'pnm', 'ppm', 'ras', 'rgb',
    'svg', 'tif', 'tiff', 'xbm', 'xpm', 'xwd'
]


@router.get('/', status_code=status.HTTP_200_OK, response_model=list[PostReadSchema], dependencies=[LIMITER_DEPENDS])
async def get_posts(user_id: int = None, user: User = Depends(get_current_active_user), session: AsyncSession = Depends(get_async_session)):

    models = []

    for post in await get_all_posts(user=user, session=session, user_id=user_id):

        if post.community_id:
            model = PostReadSchema.model_validate(post)
            model.author = CommunityShortReadSchema.model_validate(post.community)
            models.append(model)
        else:
            models.append(post)

    return models



@router.post('/', status_code=status.HTTP_201_CREATED, response_model=PostReadSchema, dependencies=[LIMITER_DEPENDS])
async def create_post(post: PostCreateSchema, user: Annotated[User, Depends(get_current_active_user)],
                      session: AsyncSession = Depends(get_async_session)):

    if post.community_id:
        community = await get_community_by_id(community_id=post.community_id, user=user, session=session)
        await validate_community_admin(user=user, community=community)

    post.author_id = user.id
    return await crud_create_post(post=post, session=session)


@router.get('/my_subscriptions', status_code=status.HTTP_200_OK, response_model=list[PostReadSchema], dependencies=[LIMITER_DEPENDS])
async def get_my_subscriptions_post(user: Annotated[User, Depends(get_current_active_user)],
                                    session: AsyncSession = Depends(get_async_session)):

    models = []

    for post in await get_posts_by_subscriptions(user=user, session=session):
        if post.community_id:
            model = PostReadSchema.model_validate(post)
            model.author = CommunityShortReadSchema.model_validate(post.community)
            models.append(model)
        else:
            models.append(post)

    return models


@router.get('/{post_id}', status_code=status.HTTP_200_OK, response_model=PostReadSchema,
            dependencies=[Depends(get_current_active_user), LIMITER_DEPENDS])
async def get_post(post_id: int, session: AsyncSession = Depends(get_async_session)):
    post = await get_post_by_id(post_id=post_id, session=session)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post not found')

    if post.community_id:
        model = PostReadSchema.model_validate(post)
        model.author = CommunityShortReadSchema.model_validate(post.community)
        return model

    return post


@router.patch('/{post_id}', status_code=status.HTTP_202_ACCEPTED, response_model=PostReadSchema, dependencies=[LIMITER_DEPENDS])
async def update_post(post_id: int, post: PostUpdateSchema, user: Annotated[User, Depends(get_current_active_user)],
                      session: AsyncSession = Depends(get_async_session)):
    old_post = await get_post_by_id(post_id=post_id, session=session)

    if old_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post not found')

    if old_post.author_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='This is not your post')

    await crud_update_post(post_id=post_id, post=post, session=session)

    return await get_post_by_id(post_id=post_id, session=session)


@router.delete('/{post_id}', status_code=status.HTTP_204_NO_CONTENT, dependencies=[LIMITER_DEPENDS])
async def delete_post(post_id: int, user: Annotated[User, Depends(get_current_active_user)],
                      session: AsyncSession = Depends(get_async_session)):
    old_post = await get_post_by_id(post_id=post_id, session=session)

    if old_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post not found')

    if old_post.author_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='This is not your post')

    await crud_delete_post(post_id=post_id, session=session)


@router.post('/upload_image/{post_id}', status_code=status.HTTP_202_ACCEPTED, response_model=PostReadSchema, dependencies=[LIMITER_DEPENDS])
async def load_image(post_id: int, current_user: Annotated[User, Depends(get_current_active_user)], image: UploadFile = File(...),
                     session: AsyncSession = Depends(get_async_session)):
    old_post = await get_post_by_id(post_id=post_id, session=session)

    index = len(old_post.images)
    image_content = await image.read()
    image_type = image.filename.split('.')[-1]

    if image_type.lower() not in IMAGE_EXTENSIONS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'Image type {image_type} is not supported')

    filename = f"{current_user.username}_{post_id}_{index}.{image_type}"

    post_image_url = os.path.join(IMAGE_POST_DIR, filename)

    if not os.path.exists(IMAGE_POST_DIR):
        os.mkdir(IMAGE_POST_DIR)

    with open(post_image_url, 'wb') as f:
        f.write(image_content)

    await upload_image_in_db_post(image_url=post_image_url, post_id=post_id, session=session)

    return await get_post_by_id(post_id=post_id, session=session)


@router.delete('/delete_image/{post_id}', status_code=status.HTTP_202_ACCEPTED, response_model=PostReadSchema,
               dependencies=[Depends(get_current_active_user), LIMITER_DEPENDS])
async def delete_image(post_id: int, image_url: str,
                       session: AsyncSession = Depends(get_async_session)):

    await delete_image_from_post(post_id=post_id, image_url=image_url, session=session)

    return await get_post_by_id(post_id=post_id, session=session)
