from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    CSRF_ALLOWED_ORIGINS: list[str] = ['*']
    JWT_SECRET: str = 'jfklajelj;kfjeklj298uf29p23u[jfo32fi2ffa;lksf]'
    JWT_ALGORITHM: str = 'HS256'
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    GOOGLE_CLIENT_ID: str = ''
    GOOGLE_CLIENT_SECRET: str = ''
    GOOGLE_REDIRECT_URI: str = ''

    MONGODB_URL: str = 'mongodb://root:password@localhost:27017'
    MONGODB_READ_URL: str = 'mongodb://root:password@localhost:27017'
    MONGODB_DATABASE: str = 'vst_realm'

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = Settings()
