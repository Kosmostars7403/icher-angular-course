from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_DB: str

    SECRET_KEY_JWT: str
    SECRET_KEY_AUTH: str

    class Config:
        env_file = ".env"


settings = Settings()
