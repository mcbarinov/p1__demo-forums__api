from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

Category = Literal["Technology", "Science", "Art"]
Role = Literal["admin", "user"]


class ErrorResponse(BaseModel):
    """Standard error response format."""

    message: str = Field(..., description="Human-readable error message")
    type: str = Field(..., description="Machine-readable error type")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"message": "Invalid credentials", "type": "authentication_error"},
                {"message": "Not authenticated", "type": "unauthorized"},
                {"message": "Forum not found", "type": "not_found"},
                {"message": "Post not found", "type": "not_found"},
                {"message": "Access denied", "type": "access_denied"},
            ]
        }
    }


class User(BaseModel):
    """User profile information."""

    id: str = Field(..., description="Unique user identifier")
    username: str = Field(..., description="Username")
    role: Role = Field(..., description="User role (admin or user)")


class UserWithPassword(User):
    """User with password (internal use only)."""

    password: str = Field(..., description="Hashed password")


class Forum(BaseModel):
    """Forum information."""

    id: str = Field(..., description="Unique forum identifier")
    slug: str = Field(..., description="URL-friendly forum identifier")
    title: str = Field(..., description="Forum title")
    description: str = Field(..., description="Forum description")
    category: Category = Field(..., description="Forum category")


class Post(BaseModel):
    """Post information."""

    id: str = Field(..., description="Unique post identifier")
    forumId: str = Field(..., description="ID of the forum this post belongs to")  # noqa: N815
    number: int = Field(..., description="Sequential post number within the forum")
    title: str = Field(..., description="Post title")
    content: str = Field(..., description="Post content")
    tags: list[str] = Field(..., description="List of tags associated with the post")
    authorId: str = Field(..., description="ID of the post author")  # noqa: N815
    createdAt: datetime = Field(..., description="Post creation timestamp")  # noqa: N815
    updatedAt: datetime | None = Field(None, description="Post last update timestamp")  # noqa: N815


class Comment(BaseModel):
    """Comment information."""

    id: str = Field(..., description="Unique comment identifier")
    postId: str = Field(..., description="ID of the post this comment belongs to")  # noqa: N815
    content: str = Field(..., description="Comment content")
    authorId: str = Field(..., description="ID of the comment author")  # noqa: N815
    createdAt: datetime = Field(..., description="Comment creation timestamp")  # noqa: N815
    updatedAt: datetime | None = Field(None, description="Comment last update timestamp")  # noqa: N815


class LoginRequest(BaseModel):
    """Request to authenticate a user."""

    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"username": "admin", "password": "admin123"},
                {"username": "john_doe", "password": "securepassword"},
            ]
        }
    }


class LoginResponse(BaseModel):
    """Response after successful authentication."""

    authToken: str = Field(..., description="Authentication token")  # noqa: N815

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"authToken": "abc123def456"},
            ]
        }
    }


class CreateForumRequest(BaseModel):
    """Request to create a new forum."""

    title: str = Field(..., description="Forum title")
    slug: str = Field(
        ...,
        description="URL-friendly unique identifier (lowercase letters, numbers, hyphens)",
        pattern="^[a-z0-9]+(?:-[a-z0-9]+)*$",
    )
    description: str = Field(..., description="Forum description")
    category: Category = Field(..., description="Forum category (Technology, Science, or Art)")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Python Discussion",
                    "slug": "python-discussion",
                    "description": "Discuss Python programming topics",
                    "category": "Technology",
                }
            ]
        }
    }


class CreatePostRequest(BaseModel):
    """Request to create a new post."""

    title: str = Field(..., description="Post title")
    content: str = Field(..., description="Post content")
    tags: list[str] = Field(default_factory=list, description="List of tags for the post")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Getting started with FastAPI",
                    "content": "FastAPI is a modern web framework...",
                    "tags": ["python", "fastapi", "tutorial"],
                }
            ]
        }
    }


class CreateCommentRequest(BaseModel):
    """Request to create a new comment."""

    content: str = Field(..., description="Comment content")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"content": "Great post! Thanks for sharing."},
            ]
        }
    }


class ChangePasswordRequest(BaseModel):
    """Request to change user password."""

    currentPassword: str = Field(..., description="Current password")  # noqa: N815
    newPassword: str = Field(..., description="New password", min_length=6)  # noqa: N815

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"currentPassword": "oldpass123", "newPassword": "newpass456"},
            ]
        }
    }


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str = Field(..., description="Response message")


class PaginatedResponse[T](BaseModel):
    """Paginated response wrapper for list endpoints."""

    items: list[T] = Field(..., description="List of items in current page")
    total_count: int = Field(..., description="Total number of items across all pages", ge=0)
    page: int = Field(..., description="Current page number (1-indexed)", ge=1)
    page_size: int = Field(..., description="Number of items per page", ge=1)
    total_pages: int = Field(..., description="Total number of pages", ge=0)
