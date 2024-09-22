import os
from typing import Annotated

from fastapi import APIRouter, status, HTTPException, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from application.account.helpers import get_current_active_user
from application.account.models import User
from application.community.crud import get_all_communities, get_community_by_id, \
    create_community as create_community_db, update_community as update_community_db, \
    delete_community as delete_community_db, delete_community_image_in_db, \
    upload_community_image_in_db
from application.community.models import ImageType
from application.community.schemas import CommunityReadSchema, CommunityCreateSchema, CommunityUpdateSchema
from application.community.validators import validate_community_admin
from database.db import get_async_session

router = APIRouter(
    tags=['community'],
    prefix='/community'
)

IMAGE_DIR = 'static/community'

IMAGE_EXTENSIONS = [
    'bmp', 'gif', 'ico', 'ief', 'jpe', 'jpeg', 'jpg',
    'pbm', 'pgm', 'png', 'pnm', 'ppm', 'ras', 'rgb',
    'svg', 'tif', 'tiff', 'xbm', 'xpm', 'xwd'
]


@router.get('/', status_code=status.HTTP_200_OK, response_model=list[CommunityReadSchema],
            dependencies=[Depends(get_current_active_user)])
async def get_communities(name: str | None = None, session: AsyncSession = Depends(get_async_session)):
    return await get_all_communities(name=name, session=session)


@router.get('/{community_id}', status_code=status.HTTP_200_OK, response_model=CommunityReadSchema,
            dependencies=[Depends(get_current_active_user)])
async def get_community(community_id: int,
                        session: AsyncSession = Depends(get_async_session)):
    if community := await get_community_by_id(community_id=community_id, session=session):
        return community

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Community not found')


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=CommunityReadSchema)
async def create_community(community: CommunityCreateSchema, user: Annotated[User, Depends(get_current_active_user)],
                           session: AsyncSession = Depends(get_async_session)):
    return await create_community_db(community=community, user=user, session=session)


@router.patch('/{community_id}', status_code=status.HTTP_200_OK, response_model=CommunityReadSchema)
async def update_community(community_id: int, community: CommunityUpdateSchema,
                           user: Annotated[User, Depends(get_current_active_user)],
                           session: AsyncSession = Depends(get_async_session)):
    old_community = await get_community_by_id(community_id=community_id, session=session)

    if not old_community:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Community not found')

    await validate_community_admin(user=user, community=old_community)

    await update_community_db(community_id=community_id, community=community, session=session)

    return await get_community_by_id(community_id=community_id, session=session)


@router.delete('/{community_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_community(community_id: int, user: Annotated[User, Depends(get_current_active_user)],
                           session: AsyncSession = Depends(get_async_session)):
    community = await get_community_by_id(community_id=community_id, session=session)

    if not community:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Community not found')

    await validate_community_admin(user=user, community=community)

    await delete_community_db(community_id=community_id, session=session)


@router.post('/{community_id}/join', status_code=status.HTTP_200_OK)
async def join_community(community_id: int, user: Annotated[User, Depends(get_current_active_user)],
                         session: AsyncSession = Depends(get_async_session)):
    community = await get_community_by_id(community_id=community_id, session=session)

    if community.admin_id == user.id:
        return {'message': f"It's your community! You are already subscribed"}

    if user.id not in community.subscribers:
        community.subscribers.append(user.id)

        await update_community_db(community_id=community_id,
                                  community=CommunityUpdateSchema(subscribers=community.subscribers),
                                  session=session)

        return {'message': f'You are now subscribed'}

    else:
        return {'message': f'You are already subscribed'}


@router.delete('/{community_id}/join', status_code=status.HTTP_202_ACCEPTED)
async def leave_community(community_id: int, user: Annotated[User, Depends(get_current_active_user)],
                          session: AsyncSession = Depends(get_async_session)):
    community = await get_community_by_id(community_id=community_id, session=session)

    if community.admin_id == user.id:
        return {'message': f"It's your community! You are not to unsubscribe"}

    if user.id in community.subscribers and community.admin_id != user.id:
        community.subscribers.remove(user.id)

        await update_community_db(community_id=community_id,
                                  community=CommunityUpdateSchema(subscribers=community.subscribers),
                                  session=session)

        return {'message': f'You are now unsubscribed'}

    else:
        return {'message': f'You are not subscribed'}


@router.post('/upload_image/{community_id}', status_code=status.HTTP_200_OK, response_model=CommunityReadSchema)
async def upload_image(community_id: int, image_type: ImageType,
                       user: Annotated[User, Depends(get_current_active_user)],
                       image: UploadFile = File(...),
                       session: AsyncSession = Depends(get_async_session)):
    community = await get_community_by_id(community_id=community_id, session=session)

    await validate_community_admin(user=user, community=community)

    image_content = await image.read()
    image_format = image.filename.split('.')[-1]

    if image_format not in IMAGE_EXTENSIONS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'Image format {image_format} is not supported')

    match image_type:
        case ImageType.BANNER:
            filename = f"{community_id}_banner.{image_format}"
        case ImageType.AVATAR:
            filename = f"{community_id}_avatar.{image_format}"

    image_url = os.path.join(IMAGE_DIR, filename)

    if not os.path.exists(IMAGE_DIR):
        os.mkdir(IMAGE_DIR)

    with open(image_url, 'wb') as f:
        f.write(image_content)

    match image_type:
        case ImageType.BANNER:
            await upload_community_image_in_db(community_id=community_id, image_url=image_url, img_type=ImageType.BANNER,
                                     session=session)
        case ImageType.AVATAR:
            await upload_community_image_in_db(community_id=community_id, image_url=image_url, img_type=ImageType.AVATAR,
                                     session=session)

    return await get_community_by_id(community_id=community_id, session=session)


@router.delete('/delete_image/{community_id}', status_code=status.HTTP_202_ACCEPTED, response_model=CommunityReadSchema)
async def delete_image(community_id: int, image_type: ImageType,
                       user: Annotated[User, Depends(get_current_active_user)],
                       session: AsyncSession = Depends(get_async_session)):
    community = await get_community_by_id(community_id=community_id, session=session)
    await validate_community_admin(user=user, community=community)

    await delete_community_image_in_db(community=community, img_type=image_type, session=session)

    return await get_community_by_id(community_id=community_id, session=session)
