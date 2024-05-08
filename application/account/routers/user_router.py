import os
from typing import Annotated
from fastapi_filter import FilterDepends
from fastapi import APIRouter, Depends, status, File, UploadFile, Query
from sqlalchemy.ext.asyncio import AsyncSession
from application.account.crud import update_user, delete_user, upload_image_in_db, get_all_users
from application.account.filters import UserFilter
from application.account.helpers import get_current_active_user
from application.account.models import User, IMAGE_DIR
from application.account.schemas.user_schemas import UserReadSchema, UserUpdateSchema, UserReadSchemaShort
from database.db import get_async_session
from fastapi_pagination import Page, paginate
from fastapi_pagination.utils import disable_installed_extensions_check

disable_installed_extensions_check()

router = APIRouter(
    tags=['account'],
    prefix='/account',
)


@router.get('/me', status_code=status.HTTP_200_OK, response_model=UserReadSchema)
async def get_me(current_user: Annotated[User, Depends(get_current_active_user)]):
    return current_user


@router.patch('/me', response_model=UserReadSchema, status_code=status.HTTP_202_ACCEPTED)
async def update_me(new_data: UserUpdateSchema, current_user: Annotated[User, Depends(get_current_active_user)],
                    session: AsyncSession = Depends(get_async_session)):
    new_data = new_data.model_dump(exclude_none=True)

    return await update_user(user=current_user, data=new_data, session=session)


@router.delete('/me', status_code=status.HTTP_204_NO_CONTENT)
async def delete_me(current_user: Annotated[User, Depends(get_current_active_user)],
                    session: AsyncSession = Depends(get_async_session)):

    await delete_user(user=current_user, session=session)

    return {'message': 'User deleted'}


@router.post('/upload_image', status_code=status.HTTP_202_ACCEPTED, response_model=UserReadSchema)
async def load_image(current_user: Annotated[User, Depends(get_current_active_user)], image: UploadFile = File(...),
                     session: AsyncSession = Depends(get_async_session)):

    image_content = await image.read()

    filename = f"{current_user.username}.jpg"

    image_url = os.path.join(IMAGE_DIR, filename)

    with open(image_url, 'wb') as f:
        f.write(image_content)

    return await upload_image_in_db(user=current_user, image_url=image_url, session=session)


@router.get('/profiles', status_code=status.HTTP_200_OK)
async def get_profiles(current_user: Annotated[User, Depends(get_current_active_user)],
                       stack: str = '',
                       user_filter: UserFilter = FilterDepends(UserFilter),
                       session: AsyncSession = Depends(get_async_session)) -> Page[UserReadSchemaShort]:
    return paginate(await get_all_users(user=current_user, session=session, user_filter=user_filter, stack=stack))
