from http import HTTPStatus
from typing import Iterable

from beanie import WriteRules
from beanie.odm.fields import PydanticObjectId
from fastapi import APIRouter, HTTPException

from core.models import Comment
from core.settings import settings

router = APIRouter(tags=['Comments'])


@router.get('/')
async def list_comments() -> Iterable[Comment]:
    return await Comment.find().to_list()


@router.post('/', status_code=HTTPStatus.CREATED)
async def create_comment(comment: Comment) -> Comment:
    await comment.insert(link_rule=WriteRules.WRITE)

    return comment


@router.get('/{id}/')
async def retrieve_comment(id: PydanticObjectId) -> Comment:
    if (comment := await Comment.find_one(Comment.id == id)) is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Comment not found.')

    return comment


@router.delete('/{id}/', status_code=204)
async def delete_comment(id: PydanticObjectId):
    if (comment := await Comment.find_one(Comment.id == id)) is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Comment not found.')

    await comment.delete(link_rule=WriteRules.WRITE)
