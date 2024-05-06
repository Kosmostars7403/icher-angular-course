from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm

from application.account.jwt import authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, \
    get_password_hash, get_current_active_user
from application.account.models import User
from application.account.schemas import Token, UserCreateSchema
from sqlalchemy.ext.asyncio import AsyncSession

from database.db import get_async_session

router = APIRouter(
    tags=['users'],
    prefix='/users',
)


@router.post("/token")
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
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.post('/register')
async def create_new_user(new_user: UserCreateSchema, session: AsyncSession = Depends(get_async_session)):
    user_data = new_user.model_dump(exclude={'password'})
    user_data['hashed_password'] = get_password_hash(new_user.password)

    user = User(**user_data)

    session.add(user)

    await session.commit()


@router.post('/test')
async def test(current_user: Annotated[User, Depends(get_current_active_user)]):
    return current_user
