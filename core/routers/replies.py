from datetime import datetime, timezone
from typing import Annotated, Literal

from beanie.odm.fields import PydanticObjectId
from beanie.operators import In
from fastapi import (
    APIRouter,
    HTTPException,
    Query,
    status,
)
from pydantic import BaseModel

from core.models import Comment

router = APIRouter(tags=['Replies'])


class CommentQueryParams(BaseModel):
    limit: int = 10
    skip: int = 0
    order_by: Literal['created_at', '-created_at', 'updated_at', '-updated_at'] = '-created_at'


@router.get('/{parent_id}/')
async def get_replies(parent_id: PydanticObjectId, query: Annotated[CommentQueryParams, Query()]):
    if not (parent_comment := await Comment.find_one(Comment.id == parent_id)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Parent Comment not found.')

    return (
        await Comment.find(In(Comment.id, parent_comment.replies))
        .skip(query.skip)
        .limit(query.limit)
        .sort(query.order_by)
        .to_list()
    )


@router.post('/{parent_id}/', status_code=status.HTTP_201_CREATED)
async def create_reply(parent_id: PydanticObjectId, comment: Comment) -> Comment:
    if not (parent_comment := await Comment.find_one(Comment.id == parent_id)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Parent Comment not found.')

    await comment.save()

    parent_comment.replies.append(comment.id)
    parent_comment.updated_at = datetime.now(tz=timezone.utc)

    await parent_comment.save()

    return comment
