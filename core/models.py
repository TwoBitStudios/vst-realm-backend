from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel


class User(BaseModel):
    id: UUID
    username: str


class Comment(BaseModel):
    id: int
    user: User
    replied_to: list[Comment]
    replies: list[Comment]


class Product(BaseModel):
    id: UUID
    comments: list[Comment]
    affiliate_links: list[str]
