from datetime import datetime
from typing import Generic, Literal, TypeVar

from pydantic import BaseModel, Field

Category = Literal["Technology", "Science", "Art"]
Role = Literal["admin", "user"]


class User(BaseModel):
    id: str
    username: str
    role: Role


class UserWithPassword(User):
    password: str


class Forum(BaseModel):
    id: str
    slug: str
    title: str
    description: str
    category: Category


class Post(BaseModel):
    id: str
    forumId: str  # noqa: N815
    number: int
    title: str
    content: str
    tags: list[str]
    authorId: str  # noqa: N815
    createdAt: datetime  # noqa: N815
    updatedAt: datetime | None = None  # noqa: N815


class Comment(BaseModel):
    id: str
    postId: str  # noqa: N815
    content: str
    authorId: str  # noqa: N815
    createdAt: datetime  # noqa: N815
    updatedAt: datetime | None = None  # noqa: N815


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    authToken: str  # noqa: N815


class CreateForumRequest(BaseModel):
    title: str
    slug: str
    description: str
    category: Category


class CreatePostRequest(BaseModel):
    title: str
    content: str
    tags: list[str] = Field(default_factory=list)


class CreateCommentRequest(BaseModel):
    content: str


class ChangePasswordRequest(BaseModel):
    currentPassword: str  # noqa: N815
    newPassword: str  # noqa: N815


class MessageResponse(BaseModel):
    message: str


T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):  # noqa: UP046
    items: list[T]
    totalCount: int  # noqa: N815
    page: int
    pageSize: int  # noqa: N815
    totalPages: int  # noqa: N815
