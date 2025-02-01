from __future__ import annotations

from datetime import datetime

from beanie import Document, Indexed
from beanie.odm.fields import PydanticObjectId
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class User(BaseModel):
    # model_config = ConfigDict(populate_by_name=True)
    id: PydanticObjectId = Field(alias='_id')
    username: str


class PrivateUser(Document):
    username: Indexed(str, unique=True)
    password: str

    class Settings:
        name = 'User'


class Comment(Document):
    message: str
    user: User
    created_at: datetime
    updated_at: datetime
    replied_to: list[Comment]
    replies: list[Comment]

    class Settings:
        name = 'Comment'


class Product(Document):
    comments: list[Comment]
    affiliate_links: list[str]

    class Settings:
        name = 'Product'
