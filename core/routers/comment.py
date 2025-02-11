from http import HTTPStatus
from typing import Iterable

from beanie import WriteRules
from beanie.odm.fields import PydanticObjectId
from bson import ObjectId
from fastapi import APIRouter, HTTPException
from datetime import datetime

from core.models import Comment, CommentSection, CreateCommentRequest
from core.settings import settings

router = APIRouter(tags=['CommentSection'])


@router.get('/{id}', status_code=HTTPStatus.OK)
async def findCommentSection(id: str) -> CommentSection:
    if (commentSection := await CommentSection.find_one(CommentSection.external_id == id, projection_model=CommentSection)) is None:
       raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Comment section not found.')
    return commentSection

# Post using id of the product to link Comment Section to Product
@router.post('/{id}', status_code=HTTPStatus.CREATED)
async def post_comment(id: str, comment: CreateCommentRequest) -> Comment:
    commentSection = await CommentSection.find_one(CommentSection.external_id == id)
    if not commentSection:
        commentSection = CommentSection(external_id=id, comments=[])

    newComment = Comment(
        id= str(ObjectId()),
        message=comment.message,
        user=None,
        created_at=datetime.now(),
        votes=0,
        votedUsers=[],
        replies=[]
    )

    commentSection.comments.insert(0, newComment)
    await commentSection.save()
    return newComment

@router.post('/{id}/replies/{comment_id}', status_code=201)
async def add_reply(id: str, comment_id: str, reply: CreateCommentRequest):
    comment_section = await CommentSection.find_one(CommentSection.external_id == id)
    if not comment_section:
        raise HTTPException(status_code=404, detail="Comment section not found")


    reply = {
        "id": str(ObjectId()),
        "message": reply.message,
        "user": None,
        "created_at": datetime.now(),
        "votes": 0,
        "votedUsers": [],
        "replies": []
    }

    result = await CommentSection.update_one(
        {"external_id": id, "comments.id": comment_id},
        {"$push": {"comments.$.replies": reply}}
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Parent comment not found")

    return reply


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
