from datetime import (
    datetime,
    timedelta,
    timezone,
)
from http import HTTPStatus
from typing import Annotated, Iterable

from beanie.odm.fields import PydanticObjectId
from beanie.odm.operators.update.general import Set
from fastapi import (
    Depends,
    HTTPException,
    status,
)
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from core.models import (
    Account,
    TokenData,
    User,
    UserInDB,
)
from core.settings import settings

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


async def update_or_create_account(
    user_id: PydanticObjectId,
    provider: str,
    provider_account_id: str,
    access_token: str,
    expires_at: datetime,
    token_type: str,
    refresh_token: str = '',
    image: str = ''
) -> Account:

    _account = Account(
        user_id=user_id,
        provider=provider,
        provider_account_id=provider_account_id,
        access_token=access_token,
        expires_at=expires_at,
        token_type=token_type,
        refresh_token=refresh_token,
        image=image
    )

    _set = Set(
        {
            Account.user_id: user_id,
            Account.provider: provider,
            Account.provider_account_id: provider_account_id,
            Account.access_token: access_token,
            Account.expires_at: expires_at,
            Account.token_type: token_type,
            Account.refresh_token: refresh_token,
            Account.image: image
        }
    )

    return await Account.find_one(Account.user_id == user_id,
                                  Account.provider_account_id == provider_account_id).upsert(
                                      _set, on_insert=_account
                                  )


async def get_or_create_user(
    given_name: str, family_name: str, email: str, email_verified: bool = False, password: str = ''
) -> UserInDB:

    if (user := await UserInDB.find_one(UserInDB.email == email)) is None:
        user = UserInDB(
            given_name=given_name,
            family_name=family_name,
            email=email,
            email_verified=email_verified,
            password=password
        )

        await user.save()

    return user


async def authenticate_user(email: str, password: str) -> UserInDB | None:
    if (user := await UserInDB.find_one(UserInDB.email == email)) is None:
        return None

    if not pwd_context.verify(password, user.password):
        return None

    return user


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    CredentialsException = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={
            "WWW-Authenticate": "Bearer"
        }
    )

    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        if (email := payload.get('sub')) is None:
            raise CredentialsException

    except JWTError:
        raise CredentialsException from None

    token_data = TokenData(email=email)
    if (user := await UserInDB.find_one(UserInDB.email == token_data.email, projection_model=User)) is None:
        raise CredentialsException

    return user


def create_access_token(data: dict) -> tuple[str, datetime]:
    to_encode = data.copy()
    expires_delta = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    expires = datetime.now(tz=timezone.utc) + expires_delta

    to_encode.update({
        'exp': expires
    })

    access_token = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

    return access_token, expires


def verify_token(
    token: str = Depends(oauth2_scheme),
    key: str = '',
    algorithms: str | Iterable[str] | None = None,
    access_token: str | None = None
):
    try:
        payload = jwt.decode(token, key=key, algorithms=algorithms, access_token=access_token)

        if payload.get('sub') is None:
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail='Token is invalid or expired')

        return payload

    except JWTError:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail='Token is invalid or expired') from None
