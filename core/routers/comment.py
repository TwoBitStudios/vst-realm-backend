from datetime import datetime, timezone
from typing import Annotated, Literal

from beanie import WriteRules
from beanie.odm.fields import PydanticObjectId
from fastapi import (
    APIRouter,
    HTTPException,
    Query,
    status,
)
from pydantic import BaseModel

from core.models import Comment

router = APIRouter(tags=['Comment'])


class CommentQueryParams(BaseModel):
    product_id: PydanticObjectId | None = None
    order_by: Literal['created_at', '-created_at', 'updated_at', '-updated_at'] = '-created_at'


@router.get('/')
async def list_comments(query: Annotated[CommentQueryParams, Query()]) -> list[Comment]:
    query_params = query.model_dump(exclude_none=True, exclude_unset=True)
    sort = query_params.pop('order_by', 'created_at')
    print(query_params)

    return await Comment.find(query_params).sort(sort).to_list()


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_comment(comment: Comment) -> Comment:
    return await comment.save()


@router.post('/{id}/', status_code=status.HTTP_201_CREATED)
async def create_reply(id: PydanticObjectId, comment: Comment) -> Comment:
    if not (parent_comment := await Comment.find_one(Comment.id == id)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Parent Comment not found.')

    await comment.save()

    parent_comment.replies.append(comment.id)
    parent_comment.updated_at = datetime.now(tz=timezone.utc)

    await parent_comment.save()

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
