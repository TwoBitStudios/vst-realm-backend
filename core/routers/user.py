from http import HTTPStatus
from typing import Iterable

from beanie.odm.fields import PydanticObjectId
from fastapi import APIRouter, HTTPException

from core.models import User, UserInDB
from core.routers.auth.utils import pwd_context

router = APIRouter(tags=['Users'])


@router.get('/')
async def list_users() -> Iterable[User]:
    return await UserInDB.find(projection_model=User).to_list()


@router.post('/', status_code=HTTPStatus.CREATED)
async def create_user(user: UserInDB) -> User:
    user.password = pwd_context.hash(user.password)
    await user.insert()
    user = await UserInDB.find_one(UserInDB.id == user.id, projection_model=User)

    return user


@router.get('/{id}/')
async def retrieve_user(id: PydanticObjectId) -> User:
    if (user := await UserInDB.find_one(UserInDB.id == id, projection_model=User)) is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='User not found.')

    return user


@router.delete('/{id}/', status_code=204)
async def delete_user(id: PydanticObjectId):
    if (user := await UserInDB.find_one(UserInDB.id == id)) is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='User not found.')

    await user.delete()
