from datetime import datetime, timezone
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from fastapi.security import OAuth2PasswordRequestForm

from core.constants import Provider
from core.models import (
    Token,
    User,
    UserInDB,
)
from core.routers.auth.utils import (
    authenticate_user,
    create_access_token,
    update_or_create_account,
)
from core.settings import settings

router = APIRouter(tags=['Auth'])


@router.post('/login/', summary='Local: Login')
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    """ The authentication endpoint to be used if authenticating with local credentials. """
    if (user := await authenticate_user(form_data.username, form_data.password)) is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect email or password',
            headers={
                'WWW-Authenticate': 'Bearer'
            }
        )

    user = await UserInDB.find_one(UserInDB.id == user.id, projection_model=User)

    access_token, expires = create_access_token(data={
        'sub': user.email
    })

    await update_or_create_account(
        user_id=user.id,
        provider=settings.LOCAL_PROVIDER_NAME,
        provider_account_id=settings.LOCAL_PROVIDER_ACCOUNT_ID,
        access_token=access_token,
        expires_at=expires,
        token_type='Bearer',
    )

    return Token(
        access_token=access_token,
        token_type='Bearer',
        expires_in=int((expires - datetime.now(tz=timezone.utc)).total_seconds()),
        provider=Provider.LOCAL,
    )
