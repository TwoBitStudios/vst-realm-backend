from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MONGODB_URL: str
    MONGODB_READ_URL: str
    MONGODB_DATABASE: str = 'vst_realm'


settings = Settings()
