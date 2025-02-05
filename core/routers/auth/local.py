from datetime import (
    datetime,
    timedelta,
    timezone,
)
from http import HTTPStatus

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt

from core.models import (
    LoginResponse,
    PrivateUser,
    User,
)
from core.routers.auth.utils import authenticate_user, get_or_create_account
from core.routers.auth.utils import verify_token as _verify_token
from core.settings import settings

router = APIRouter(tags=['Auth: Local'])


@router.post('/login/')
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> LoginResponse:
    """ The authentication endpoint to be used if authenticating with local credentials. """
    user = await authenticate_user(form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Failed to authenticate',
            headers={
                'WWW-Authenticate': 'Bearer'
            }
        )

    access_token, expires = create_access_token(
        data={
            'sub': user.email
        }
    )

    user = await PrivateUser.find_one(PrivateUser.id == user.id, projection_model=User)

    await get_or_create_account(
        user.id,
        provider=settings.LOCAL_PROVIDER_NAME,
        provider_account_id=settings.LOCAL_PROVIDER_ACCOUNT_ID,
        access_token=access_token,
        expires_at=expires,
        token_type='bearer',
    )

    return LoginResponse(**{
        'user': user,
        'access_token': access_token,
        'expires_in': int((expires - datetime.now(tz=timezone.utc)).total_seconds()),
        'token_type': 'bearer',
    })


@router.get('/verify-token/{token}/')
async def verify_token(token: str) -> dict:
    """ Verifies a locally-provided authentication token. """
    _verify_token(token, settings.JWT_SECRET, algorithms=settings.JWT_ALGORITHM)

    return {
        'message': 'Token is valid'
    }


def create_access_token(data: dict) -> tuple[str, datetime]:
    to_encode = data.copy()
    expires_delta = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    expires = datetime.now(tz=timezone.utc) + expires_delta

    to_encode.update({
        'exp': expires
    })

    access_token = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

    return access_token, expires
