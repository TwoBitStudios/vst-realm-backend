from datetime import timedelta
from http import HTTPStatus
from typing import Iterable

from beanie.odm.fields import PydanticObjectId
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from fastapi.security import OAuth2PasswordRequestForm

from core.models import PrivateUser, User
from core.routers.utils import (
    authenticate_user,
    create_access_token,
    pwd_context,
    verify_token,
)
from core.settings import settings

router = APIRouter(tags=['Users'])


@router.get('/')
async def list_users() -> Iterable[User]:
    return await PrivateUser.find(projection_model=User).to_list()


@router.post('/', status_code=HTTPStatus.CREATED)
async def create_user(user: PrivateUser) -> User:
    user.password = pwd_context.hash(user.password)
    await user.insert()
    user = await PrivateUser.find_one(PrivateUser.id == user.id, projection_model=User)

    return user


@router.get('/{id}/')
async def retrieve_user(id: PydanticObjectId) -> User:
    if (user := await PrivateUser.find_one(PrivateUser.id == id, projection_model=User)) is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='User not found.')

    return user


@router.delete('/{id}/', status_code=204)
async def delete_user(id: PydanticObjectId):
    if (user := await PrivateUser.find_one(PrivateUser.id == id)) is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='User not found.')

    await user.delete()


@router.post('/token/')
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
            'sub': user.username
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
