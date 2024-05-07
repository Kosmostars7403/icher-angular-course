from typing import Annotated

from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError

from application.account.schemas import UserReadSchema
from .jwt import SECRET_KEY, ALGORITHM, oauth2_scheme, ACCESS_TOKEN_TYPE, REFRESH_TOKEN_TYPE
from application.account.crud import get_user
from .models import User
from .validation import validate_token_type

CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

TOKEN_EXCEPTION = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Invalid token",
)


def get_current_token_payload(token: str = Depends(oauth2_scheme)) -> dict:

    try:
        return jwt.decode(
            token, SECRET_KEY, algorithms=[ALGORITHM]
        )

    except JWTError:
        raise TOKEN_EXCEPTION


async def get_user_by_token_sub(payload: dict):
    username: str = payload.get("sub")

    user = await get_user(username=username)

    if user is None:
        raise CREDENTIALS_EXCEPTION

    return user


class UserGetterFromToken:
    def __init__(self, token_type: str):
        self.token_type = token_type

    async def __call__(self, payload: dict = Depends(get_current_token_payload)):
        await validate_token_type(payload, self.token_type)
        return await get_user_by_token_sub(payload)


get_current_auth_user = UserGetterFromToken(ACCESS_TOKEN_TYPE)
get_current_user_from_refresh = UserGetterFromToken(REFRESH_TOKEN_TYPE)


async def get_current_active_user(
        current_user: Annotated[UserReadSchema, Depends(get_current_auth_user)],
):

    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    return current_user
