from datetime import timedelta, timezone, datetime

from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext

from settings import settings

SECRET_KEY = settings.SECRET_KEY_AUTH
ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS

ACCESS_TOKEN_TYPE = 'access'
REFRESH_TOKEN_TYPE = 'refresh'

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def create_jwt(token_type: str, token_data: dict, expires_delta: timedelta | None = timedelta(minutes=15)) -> str:
    jwt_payload = {
        "type": token_type,
    }
    jwt_payload.update(token_data)

    expire = datetime.now(timezone.utc) + expires_delta

    jwt_payload.update({"exp": expire})

    return jwt.encode(jwt_payload, SECRET_KEY, algorithm=ALGORITHM)


def create_access_token(data: dict):
    return create_jwt(token_type=ACCESS_TOKEN_TYPE,
                      token_data=data,
                      expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))


def create_refresh_token(data: dict):
    return create_jwt(token_type=REFRESH_TOKEN_TYPE,
                      token_data=data,
                      expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
