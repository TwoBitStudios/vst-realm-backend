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
    given_name: str
    family_name: str
    email: str
    email_verified: bool = False


class PrivateUser(Document):
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
    type: str
    provider: str
    provider_account_id: str
    refresh_token: str
    access_token: str
    expires_at: int
    token_type: str
    image: str

    class Settings:
        name = 'Account'


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
