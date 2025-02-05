
from datetime import datetime
from http import HTTPStatus
from typing import Iterable

from beanie.odm.fields import PydanticObjectId
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from core.models import Account, PrivateUser

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


async def get_or_create_account(
        user_id: PydanticObjectId,
        provider: str,
        provider_account_id: str,
        access_token: str,
        expires_at: datetime,
        token_type: str,
        refresh_token: str = '',
        image: str = '') -> Account:

    if (account := await Account.find_one(Account.user_id == user_id, Account.provider_account_id == provider_account_id)) is None:
        account = Account(
            user_id=user_id,
            provider=provider,
            provider_account_id=provider_account_id,
            access_token=access_token,
            expires_at=expires_at,
            token_type=token_type,
            refresh_token=refresh_token,
            image=image
        )

        await account.save()

    return account


async def get_or_create_user(
        given_name: str,
        family_name: str,
        email: str,
        email_verified: bool = False,
        password: str = '') -> PrivateUser:

    if (user := await PrivateUser.find_one(PrivateUser.email == email)) is None:
        user = PrivateUser(
            given_name=given_name,
            family_name=family_name,
            email=email,
            email_verified=email_verified,
            password=password
        )

        await user.save()

    return user


async def authenticate_user(email: str, password: str) -> PrivateUser | None:
    if (user := await PrivateUser.find_one(PrivateUser.email == email)) is None:
        return None

    if not pwd_context.verify(password, user.password):
        return None

    return user


def verify_token(token: str = Depends(oauth2_scheme), key: str = '', algorithms: str | Iterable[str] | None = None, access_token: str | None = None):
    try:
        payload = jwt.decode(token, key=key, algorithms=algorithms, access_token=access_token)

        if payload.get('sub') is None:
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail='Token is invalid or expired')

        return payload

    except JWTError:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail='Token is invalid or expired') from None
