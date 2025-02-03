from datetime import (
    datetime,
    timedelta,
    timezone,
)
from http import HTTPStatus

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from core.models import PrivateUser
from core.settings import settings

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


async def authenticate_user(username: str, password: str) -> PrivateUser | None:
    if (user := await PrivateUser.find_one(PrivateUser.username == username)) is None:
        return None

    if not pwd_context.verify(password, user.password):
        return None

    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(tz=timezone.utc) + expires_delta

    else:
        expire = datetime.now(tz=timezone.utc) + timedelta(minutes=15)

    to_encode.update({
        'exp': expire
    })
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

    return encoded_jwt


def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        if payload.get('sub') is None:
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail='Token is invalid or expired')

        return payload

    except JWTError:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail='Token is invalid or expired') from None
