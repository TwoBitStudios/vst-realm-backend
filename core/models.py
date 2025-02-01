from __future__ import annotations

from datetime import datetime
from typing import Any

from beanie import Document, Indexed
from pydantic import BaseModel


class User(Document):
    username: Indexed(str, unique=True)
    password: str

    class Settings:
        name = 'User'


class PublicUser(BaseModel):
    id: Any
    username: str


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
