from typing import Annotated

from fastapi import APIRouter, Depends, status

from application.account.crud import update_user, delete_user
from application.account.helpers import get_current_active_user
from application.account.models import User
from application.account.schemas import UserUpdateSchema, UserReadSchema
from application.account.validation import get_password_hash

router = APIRouter(
    tags=['users'],
    prefix='/users',
)


@router.get('/me', status_code=status.HTTP_200_OK, response_model=UserReadSchema)
async def get_me(current_user: Annotated[User, Depends(get_current_active_user)]):
    return current_user


@router.patch('/me', response_model=UserReadSchema, status_code=status.HTTP_202_ACCEPTED)
async def update_me(new_data: UserUpdateSchema, current_user: Annotated[User, Depends(get_current_active_user)]):
    new_data = new_data.model_dump(exclude_none=True)

    if new_data.get('password'):
        new_data['hashed_password'] = get_password_hash(new_data.pop('password'))

    return await update_user(current_user, new_data)


@router.delete('/me', status_code=status.HTTP_204_NO_CONTENT)
async def delete_me(current_user: Annotated[User, Depends(get_current_active_user)]):
    await delete_user(current_user)

    return {'message': 'User deleted'}
