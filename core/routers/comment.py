from beanie import WriteRules
from beanie.odm.fields import PydanticObjectId
from fastapi import (
    APIRouter,
    HTTPException,
    status,
)

from core.models import Comment

router = APIRouter(tags=['Comment'])


@router.get('/')
async def list_comments() -> list[Comment]:
    return Comment.find()


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_comment(comment: Comment) -> Comment:
    return await comment.save()


@router.get('/{id}/')
async def retrieve_comment(id: PydanticObjectId) -> Comment:
    if (comment := await Comment.find_one(Comment.id == id)) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Comment not found.')

    return comment


@router.delete('/{id}/', status_code=204)
async def delete_comment(id: PydanticObjectId):
    if (comment := await Comment.find_one(Comment.id == id)) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Comment not found.')

    await comment.delete(link_rule=WriteRules.WRITE)
