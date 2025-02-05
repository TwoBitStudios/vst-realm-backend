from datetime import timedelta
from http import HTTPStatus

import requests
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt

from core.models import (
    Account,
    PrivateUser,
    User,
)
from core.routers.utils import (
    authenticate_user,
    create_access_token,
    pwd_context,
    verify_token,
)
from core.settings import settings

router = APIRouter(tags=['Auth'])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post('/login/local/')
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()) -> dict:
    user = await authenticate_user(form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Failed to authenticate',
            headers={
                'WWW-Authenticate': 'Bearer'
            }
        )

    access_token_expires = timedelta(settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            'sub': user.email
        }, expires_delta=access_token_expires
    )

    user = await PrivateUser.find_one(PrivateUser.id == user.id, projection_model=User)
    return {
        'access_token': access_token,
        'token_type': 'bearer',
        'user': user
    }


@router.get('/verify-token/{token}/')
async def verify_user_token(token: str) -> dict:
    verify_token(token)

    return {
        'message': 'Token is valid'
    }


@router.get("/login/google/")
async def login_google():
    return {
        "url":
            f"https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={settings.GOOGLE_CLIENT_ID}&redirect_uri={settings.GOOGLE_REDIRECT_URI}&scope=openid%20profile%20email&access_type=offline"
    }


@router.get("/auth/google/")
async def auth_google(code: str):
    token_url = "https://accounts.google.com/o/oauth2/token"
    data = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    response = requests.post(token_url, data=data)
    access_token = response.json().get("access_token")
    user_info = requests.get(
        "https://www.googleapis.com/oauth2/v1/userinfo", headers={
            "Authorization": f"Bearer {access_token}"
        }
    )
    return user_info.json()


@router.get("/token/")
async def get_token(token: str = Depends(oauth2_scheme)):
    return jwt.decode(token, settings.GOOGLE_CLIENT_SECRET, algorithms=["HS256"])
