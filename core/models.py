from __future__ import annotations

from datetime import datetime

from beanie import (
    BackLink,
    Document,
    Indexed,
    Link,
)
from beanie.odm.fields import PydanticObjectId
from pydantic import BaseModel, Field


class User(BaseModel):
    id: PydanticObjectId = Field(alias='_id')
    first_name: str
    last_name: str
    username: str


class PrivateUser(Document):
    first_name: str
    last_name: str
    username: Indexed(str, unique=True)
    password: str
    comments: list[BackLink['Comment']] = Field(list(), original_field='user')

    class Settings:
        name = 'User'


class Comment(Document):
    message: str
    user: Link[PrivateUser]
    product: Link[Product]
    created_at: datetime = datetime.now()
    updated_at: datetime | None = None

    class Settings:
        name = 'Comment'


class Product(Document):
    external_id: str
    affiliate_links: list[str]
    comments: list[BackLink['Comment']] = Field(list(), original_field='product')

    class Settings:
        name = 'Product'
