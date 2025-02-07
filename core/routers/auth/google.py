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
from requests.exceptions import RequestException

from core.models import LoginResponse, User
from core.routers.auth.utils import get_or_create_account, get_or_create_user
from core.routers.auth.utils import verify_token as _verify_token
from core.settings import settings

logger = logging.getLogger(__name__)

router = APIRouter(tags=['Auth: Google'])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


@router.get('/login/')
async def login_google():
    """ The authentication endpoint to be used if authenticating with Google. """
    return {
        'url':
            f'https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={settings.GOOGLE_CLIENT_ID}&redirect_uri={settings.GOOGLE_REDIRECT_URI}&scope=openid%20profile%20email&access_type=offline'
    }


@router.get('/verify-token/{token}/')
async def verify_token(token: str) -> dict:
    """ Verifies an authentication token provided by Google. """
    _verify_token(token, settings.GOOGLE_CLIENT_SECRET, algorithms=['HS256'])

    return {
        'message': 'Token is valid'
    }


@router.get('/authenticate/')
async def auth_google(code: str) -> LoginResponse:
    token_data = get_google_access_token(code)

    if (access_token := token_data.get('access_token')) is None:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail='No access token was provided.')

    if (user_data := get_google_user_data(access_token)) is None:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail='Could not authenticate.')

    user = User.from_private_user(
        await get_or_create_user(
            given_name=user_data.get('given_name'),
            family_name=user_data.get('family_name'),
            email=user_data.get('email'),
            email_verified=user_data.get('verified_email'),
        )
    )

    expires_at = datetime.now(tz=timezone.utc) - timedelta(seconds=token_data.get('expires_in', 0))
    await get_or_create_account(
        user.id,
        provider=settings.LOCAL_PROVIDER_NAME,
        provider_account_id=settings.LOCAL_PROVIDER_ACCOUNT_ID,
        access_token=access_token,
        expires_at=expires_at,
        token_type='bearer',
    )

    return RedirectResponse(f'{settings.FRONTEND_LOGIN_REDIRECT_URI}?access_token={access_token}')

    # return LoginResponse(
    #     **{
    #         'user': user,
    #         'access_token': access_token,
    #         'expires_in': token_data.get('expires_in', 0),
    #         'token_type': token_data.get('token_type', 'bearer'),
    #         'scope': token_data.get('scope'),
    #         'refresh_token': token_data.get('refresh_token'),
    #         'id_token': token_data.get('id_token'),
    #     }
    # )


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
