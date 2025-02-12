from __future__ import annotations

from datetime import datetime

import pymongo
from beanie import (
    BackLink,
    Document,
    Indexed,
)
from beanie.odm.fields import PydanticObjectId
from pydantic import BaseModel, Field
from pymongo import IndexModel

from core.constants import CommentAction, Provider


class User(BaseModel):
    id: PydanticObjectId = Field(alias='_id')
    given_name: str
    family_name: str
    email: str
    email_verified: bool = False

    @classmethod
    def from_db(cls, _user: UserInDB):
        return cls(
            _id=_user.id,
            given_name=_user.given_name,
            family_name=_user.family_name,
            email=_user.email,
            email_verified=_user.email_verified,
        )


class UserInDB(Document):
    given_name: str
    family_name: str
    email: Indexed(str, unique=True)
    email_verified: bool = False
    password: str
    comments: list[BackLink['Comment']] = Field(list(), original_field='user')

    class Settings:
        name = 'User'


class Account(Document):
    user_id: PydanticObjectId
    provider: str
    provider_account_id: str
    access_token: str
    expires_at: datetime
    token_type: str
    refresh_token: str = ''
    image: str = ''

    class Settings:
        name = 'Account'
        indexes = [
            IndexModel(
                [('user_id', pymongo.ASCENDING), ('provider_account_id', pymongo.ASCENDING)],
                name='user_id__provider_account_id__unique_together',
                unique=True,
            )
        ]


class CommentVote(Document):
    action: CommentAction
    comment_id: PydanticObjectId
    user_id: PydanticObjectId


class Comment(Document):
    message: str
    user_id: PydanticObjectId
    product_id: PydanticObjectId
    created_at: datetime = datetime.now()
    updated_at: datetime | None = None
    replies: list[PydanticObjectId] = []

    class Settings:
        name = 'Comment'


class Product(Document):
    external_id: str
    affiliate_links: list[str]
    comments: list[BackLink['Comment']] = Field(list(), original_field='product')

    class Settings:
        name = 'Product'


class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int = 0
    provider: Provider


class TokenData(BaseModel):
    email: str | None = None
