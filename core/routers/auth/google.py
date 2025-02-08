import logging
from datetime import (
    datetime,
    timedelta,
    timezone,
)
from http import HTTPStatus
from json import JSONDecodeError

import requests
from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from requests.exceptions import RequestException

from core.constants import Provider
from core.models import Token, User
from core.routers.auth.utils import (
    create_access_token,
    get_or_create_user,
    update_or_create_account,
)
from core.settings import settings

logger = logging.getLogger(__name__)

router = APIRouter(tags=['Auth: Google'])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


class GoogleAuthenticate(BaseModel):
    code: str
    redirect_uri: str | None = None


@router.get('/login/')
async def login():
    """ The authentication endpoint to be used if authenticating with Google. """
    return {
        'url':
            f'https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={settings.GOOGLE_CLIENT_ID}&redirect_uri={settings.GOOGLE_REDIRECT_URI}&scope=openid%20profile%20email&access_type=offline'
    }


@router.get('/authenticate/')
async def auth_google(code: str, redirect_uri: str | None = None) -> Token:
    token_data = get_google_access_token(code)

    if (google_access_token := token_data.get('access_token')) is None:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail='No access token was provided.')

    if (user_data := get_google_user_data(google_access_token)) is None:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail='Could not authenticate.')

    user = User.from_db(
        await get_or_create_user(
            given_name=user_data.get('given_name'),
            family_name=user_data.get('family_name'),
            email=user_data.get('email'),
            email_verified=user_data.get('verified_email'),
        )
    )

    expires_at = datetime.now(tz=timezone.utc) - timedelta(seconds=token_data.get('expires_in', 0))

    await update_or_create_account(
        user_id=user.id,
        provider=Provider.GOOGLE,
        provider_account_id=user_data.get('id'),
        access_token=google_access_token,
        expires_at=expires_at,
        token_type=token_data.get('token_type'),
        refresh_token=token_data.get('refresh_token', ''),
        image=user_data.get('picture', '')
    )

    access_token, expires = create_access_token(data={
        'sub': user.email
    })

    token = Token(
        access_token=access_token,
        token_type='Bearer',
        expires_in=int((expires - datetime.now(tz=timezone.utc)).total_seconds()),
        provider=Provider.GOOGLE,
    )

    params = f'?access_token={token.access_token}&token_type={token.token_type}&expires_in={token.expires_in}&provider={token.provider.value}'
    redirect = f'{redirect_uri or settings.FRONTEND_LOGIN_REDIRECT_URI}{params}'

    return RedirectResponse(redirect)


def get_google_access_token(code: str) -> dict:
    token_url = 'https://accounts.google.com/o/oauth2/token'
    data = {
        'code': code,
        'client_id': settings.GOOGLE_CLIENT_ID,
        'client_secret': settings.GOOGLE_CLIENT_SECRET,
        'redirect_uri': settings.GOOGLE_REDIRECT_URI,
        'grant_type': 'authorization_code',
    }

    try:
        response = requests.post(token_url, data=data)

    except RequestException as exc:
        logger.error(
            f'Did not retrieve access token from Google.  Reason: Encountered an error during the request.  Exception: {exc}'
        )
        return None

    try:
        token_data = response.json()

    except JSONDecodeError as exc:
        logger.error(
            f'Did not retrieve access token from Google.  Reason: Could not read the response data.  Exception: {exc}'
        )
        return None

    return token_data


def get_google_user_data(access_token: str) -> dict:
    try:
        response = requests.get(
            'https://www.googleapis.com/oauth2/v1/userinfo', headers={
                'Authorization': f'Bearer {access_token}'
            }
        )

    except RequestException as exc:
        logger.error(
            f'Did not retrieve user data from Google.  Reason: Encountered an error during the request.  Exception: {exc}'
        )
        return None

    try:
        user_info = response.json()

    except JSONDecodeError as exc:
        logger.error(
            f'Did not retrieve user data from Google.  Reason: Could not read the response data.  Exception: {exc}'
        )
        return None

    return user_info
