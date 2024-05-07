from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from application.account.helpers import get_current_user_from_refresh, get_current_active_user
from application.account.jwt import create_access_token, create_refresh_token
from application.account.models import User
from application.account.schemas import Token, UserReadSchema, UserCreateSchema
from application.account.validation import get_password_hash, authenticate_user
from database.db import get_async_session

router = APIRouter(
    tags=['users'],
    prefix='/users',
)


@router.post("/token", response_model=Token)
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user.username}
    )

    refresh_token = create_refresh_token(
        data={"sub": user.username}
    )

    return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")


@router.post('/refresh', response_model=Token, response_model_exclude_none=True, )
async def refresh_token(user: UserReadSchema = Depends(get_current_user_from_refresh)):
    access_token = create_access_token(
        data={"sub": user.username}
    )
    return Token(access_token=access_token, token_type="bearer")


@router.post('/logout', dependencies=[Depends(get_current_active_user)])
async def logout():
    return {'message': 'logout'}


@router.post('/register')
async def create_new_user(new_user: UserCreateSchema, session: AsyncSession = Depends(get_async_session)):
    user_data = new_user.model_dump(exclude={'password'})
    user_data['hashed_password'] = get_password_hash(new_user.password)

    user = User(**user_data)

    session.add(user)

    await session.commit()
