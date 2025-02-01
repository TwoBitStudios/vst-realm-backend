from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    CSRF_ALLOWED_ORIGINS: list[str] = ['http://localhost:5173']
    JWT_SECRET: str = 'fkjahekjkfhekafjlekajkfhioej2nf982hhf3whjlH@#j32l;rj'
    JWT_ALGORITHM: str = 'HS256'
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    MONGODB_URL: str = 'mongodb://localhost:27017'
    MONGODB_READ_URL: str = 'mongodb://localhost:27017'
    MONGODB_DATABASE: str = 'vst_realm'


settings = Settings()
