from http import HTTPStatus
from typing import Iterable

from beanie.odm.fields import PydanticObjectId
from fastapi import APIRouter, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext

from core.models import PrivateUser, User
from core.settings import settings

router = APIRouter(tags=['Users'])

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


@router.get('/')
async def list_users() -> Iterable[User]:
    return await PrivateUser.find(projection_model=User).to_list()


@router.post('/', status_code=HTTPStatus.CREATED)
async def create_user(user: PrivateUser) -> User:
    user.password = pwd_context.hash(user.password)
    await user.insert()
    user = User(_id=user.id, username=user.username)

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
