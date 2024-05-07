from application.account.jwt import pwd_context
from application.account.crud import get_user
from fastapi import HTTPException, status


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def authenticate_user(username: str, password: str):
    user = await get_user(username=username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


async def validate_token_type(payload: dict, token_type: str) -> bool:
    current_token_type = payload.get("type")

    if current_token_type == token_type:
        return True

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"Invalid token type {current_token_type!r} expected {token_type!r}",
    )
