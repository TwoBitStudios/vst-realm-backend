from beanie import WriteRules
from beanie.odm.fields import PydanticObjectId
from fastapi import (
    APIRouter,
    HTTPException,
    status,
)
from datetime import datetime

from core.models import Comment

router = APIRouter(tags=['Comment'])


@router.get('/')
async def list_comments() -> list[Comment]:
    return await Comment.find().to_list()

@router.get('/{productId}/')
async def list_comments(productId: PydanticObjectId) -> list[Comment]:
    return await Comment.find(Comment.product_id == productId).to_list()

@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_comment(comment: Comment) -> Comment:
    return await comment.save()

@router.post('/{commentId}/', status_code=status.HTTP_201_CREATED)
async def create_reply(commentId: str, comment: Comment) -> Comment:
    parentComment = await Comment.find_one({'_id': PydanticObjectId(commentId)})
    if not parentComment:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Parent Comment not found.')
    
    await comment.save()

    parentComment.replies.append(comment.id)
    parentComment.updated_at = datetime.now()

    await parentComment.save()

    return comment



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
