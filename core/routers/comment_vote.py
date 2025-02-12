from beanie import WriteRules
from beanie.odm.fields import PydanticObjectId
from fastapi import (
    APIRouter,
    HTTPException,
    status,
)

from core.models import CommentVote

router = APIRouter(tags=['CommentVote'])


@router.get('/')
async def list_comments() -> list[CommentVote]:
    return CommentVote.find()


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_comment(comment: CommentVote) -> CommentVote:
    return await comment.save()


@router.get('/{id}/')
async def retrieve_comment(id: PydanticObjectId) -> CommentVote:
    if (comment := await CommentVote.find_one(CommentVote.id == id)) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='CommentVote not found.')

    return comment


@router.delete('/{id}/', status_code=204)
async def delete_comment(id: PydanticObjectId):
    if (comment := await CommentVote.find_one(CommentVote.id == id)) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='CommentVote not found.')

    await comment.delete(link_rule=WriteRules.WRITE)
