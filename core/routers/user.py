from typing import Iterable

from beanie.odm.fields import PydanticObjectId
from fastapi import APIRouter, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext

from core import models
from core.models import PublicUser, User
from core.settings import settings

router = APIRouter()

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


@router.get('/', tags=['users'])
async def list_users() -> Iterable[PublicUser]:
    users = await User.find().to_list()
    return [PublicUser(id=str(user.id), username=user.username) for user in users]


@router.post('/')
async def create_user(user: User):
    hashed_password = pwd_context.hash(user.password)

    user = User(username=user.username, password=hashed_password)
    await user.insert()

    _user = PublicUser(id=str(user.id), username=user.username)
    return _user


@router.get('/{id}/')
async def get_user(id: PydanticObjectId) -> PublicUser:
    if (user := await User.find_one(User.id == id)) is None:
        raise HTTPException(status_code=404, detail='User not found.')

    _user = PublicUser(id=str(user.id), username=user.username)
    return _user


@router.delete('/{id}/')
async def delete_user(id: PydanticObjectId):
    if (user := await User.find_one(User.id == id)) is None:
        raise HTTPException(status_code=404, detail='User not found.')

    await user.delete()
