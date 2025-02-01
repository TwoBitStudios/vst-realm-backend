from http import HTTPStatus
from typing import Iterable

from beanie.odm.fields import PydanticObjectId
from fastapi import APIRouter, HTTPException

from core.models import (
    Comment,
    PrivateUser,
    Product,
)
from core.settings import settings

router = APIRouter(tags=['Comments'])


@router.get('/')
async def list_comments() -> Iterable[Comment]:
    return await Comment.find().to_list()


@router.post('/', status_code=HTTPStatus.CREATED)
async def create_comment(comment: Comment):
    print(comment.id)
    # user = await PrivateUser.find_one(PrivateUser.id == comment.user)
    # await comment.insert()

    # return comment


@router.get('/{id}/')
async def retrieve_comment(id: PydanticObjectId) -> Comment:
    if (comment := await Comment.find_one(Comment.id == id)) is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Comment not found.')

    return comment


@router.delete('/{id}/', status_code=204)
async def delete_comment(id: PydanticObjectId):
    if (comment := await Comment.find_one(Comment.id == id)) is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Comment not found.')

    await comment.delete()
