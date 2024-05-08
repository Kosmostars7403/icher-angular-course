from typing import Annotated

from fastapi import APIRouter, Depends, status, File
from sqlalchemy.ext.asyncio import AsyncSession

from application.account.crud import update_user, delete_user
from application.account.helpers import get_current_active_user
from application.account.models import User
from application.account.schemas.user_schemas import UserReadSchema, UserUpdateSchema
from database.db import get_async_session

router = APIRouter(
    tags=['users'],
    prefix='/users',
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


@router.post('/load_image', status_code=status.HTTP_202_ACCEPTED)
async def load_image(current_user: Annotated[User, Depends(get_current_active_user)]):

    return {'message': 'Image uploaded'}
