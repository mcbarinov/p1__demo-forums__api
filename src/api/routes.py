import math
import os
import uuid
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Response, status

from .data import (
    mock_comments,
    mock_forums,
    mock_posts,
    mock_users,
    sessions,
)
from .deps import CurrentUserDep
from .models import (
    ChangePasswordRequest,
    Comment,
    CreateCommentRequest,
    CreateForumRequest,
    CreatePostRequest,
    ErrorResponse,
    Forum,
    LoginRequest,
    LoginResponse,
    MessageResponse,
    PaginatedResponse,
    Post,
    User,
)

# Secure flag for cookies: True in production, False in development
# In production, reverse proxy (Caddy/Nginx) terminates SSL
SECURE_COOKIES = os.getenv("ENVIRONMENT", "development") == "production"

# Routers with tags for OpenAPI grouping
auth_router = APIRouter(tags=["auth"])
profile_router = APIRouter(tags=["profile"])
forums_router = APIRouter(tags=["forums"])
posts_router = APIRouter(tags=["posts"])
comments_router = APIRouter(tags=["comments"])
users_router = APIRouter(tags=["users"])


@auth_router.post(
    "/auth/login",
    summary="User login",
    description="Authenticate with username and password. Returns a session token and sets an HttpOnly cookie.",
    operation_id="loginUser",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Login successful"},
        401: {"model": ErrorResponse, "description": "Invalid credentials"},
    },
)
def login(credentials: LoginRequest, response: Response) -> LoginResponse:
    """Login with username and password"""
    user = next(
        (u for u in mock_users if u.username == credentials.username and u.password == credentials.password),
        None,
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    session_id = str(uuid.uuid4())
    sessions[session_id] = User(id=user.id, username=user.username, role=user.role)

    # Set cookie for browser clients
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        secure=SECURE_COOKIES,
        samesite="lax",
        path="/",
        max_age=604800,  # 7 days
    )

    # Return token for API clients
    return LoginResponse(authToken=session_id)


@auth_router.post(
    "/auth/logout",
    summary="User logout",
    description="Logout and invalidate the current session. Clears the session cookie.",
    operation_id="logoutUser",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Logout successful"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
    },
)
def logout(current_user: CurrentUserDep, response: Response) -> MessageResponse:
    """Logout and invalidate session"""
    token_to_remove = None
    for token, user in sessions.items():
        if user.id == current_user.id:
            token_to_remove = token
            break

    if token_to_remove:
        del sessions[token_to_remove]

    response.delete_cookie(key="session_id", path="/", secure=SECURE_COOKIES, samesite="lax")

    return MessageResponse(message="Logged out successfully")


@profile_router.get(
    "/profile",
    summary="Get user profile",
    description="Get the profile information of the currently authenticated user.",
    operation_id="getUserProfile",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "User profile retrieved successfully"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
    },
)
def get_profile(current_user: CurrentUserDep) -> User:
    """Get current user profile"""
    return current_user


@profile_router.post(
    "/profile/change-password",
    summary="Change password",
    description="Change the password for the currently authenticated user. Requires current password verification.",
    operation_id="changeUserPassword",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Password changed successfully"},
        400: {"model": ErrorResponse, "description": "Current password is incorrect"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        404: {"model": ErrorResponse, "description": "User not found"},
    },
)
def change_password(request: ChangePasswordRequest, current_user: CurrentUserDep) -> MessageResponse:
    """Change password"""
    user = next((u for u in mock_users if u.id == current_user.id), None)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user.password != request.currentPassword:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    user.password = request.newPassword
    return MessageResponse(message="Password changed successfully")


@forums_router.get(
    "/forums",
    summary="List all forums",
    description="Get a list of all available forums.",
    operation_id="listForums",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "List of forums"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
    },
)
def get_forums(_current_user: CurrentUserDep) -> list[Forum]:
    """Get all forums"""
    return mock_forums


@forums_router.post(
    "/forums",
    summary="Create new forum",
    description="Create a new forum with a unique slug, title, description, and category.",
    operation_id="createForum",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Forum created successfully"},
        400: {"model": ErrorResponse, "description": "Forum with this slug already exists"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
    },
)
def create_forum(forum_data: CreateForumRequest, _current_user: CurrentUserDep) -> Forum:
    """Create new forum"""
    existing = next((f for f in mock_forums if f.slug == forum_data.slug), None)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A forum with this slug already exists",
        )

    new_forum = Forum(
        id=str(uuid.uuid4()),
        slug=forum_data.slug,
        title=forum_data.title,
        description=forum_data.description,
        category=forum_data.category,
    )
    mock_forums.append(new_forum)
    return new_forum


@posts_router.get(
    "/forums/{slug}/posts",
    summary="List forum posts",
    description="Get paginated posts for a specific forum, sorted by creation date (newest first).",
    operation_id="listForumPosts",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Paginated list of posts"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        404: {"model": ErrorResponse, "description": "Forum not found"},
    },
)
def get_posts(
    slug: str,
    _current_user: CurrentUserDep,
    page: Annotated[int, Query(ge=1, description="Page number (1-indexed)")] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, description="Number of items per page")] = 10,
) -> PaginatedResponse[Post]:
    """Get posts for a forum with pagination"""
    forum = next((f for f in mock_forums if f.slug == slug), None)
    if forum is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Forum not found",
        )

    forum_posts = [p for p in mock_posts if p.forumId == forum.id]
    forum_posts.sort(key=lambda p: p.createdAt, reverse=True)

    total_count = len(forum_posts)
    total_pages = math.ceil(total_count / page_size)

    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    items = forum_posts[start_index:end_index]

    return PaginatedResponse(
        items=items,
        total_count=total_count,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@posts_router.get(
    "/forums/{slug}/posts/{post_number}",
    summary="Get single post",
    description="Get a specific post by its sequential number within a forum.",
    operation_id="getForumPost",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Post retrieved successfully"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        404: {"model": ErrorResponse, "description": "Forum or post not found"},
    },
)
def get_post(slug: str, post_number: int, _current_user: CurrentUserDep) -> Post:
    """Get single post by number"""
    forum = next((f for f in mock_forums if f.slug == slug), None)
    if forum is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Forum not found",
        )

    post = next((p for p in mock_posts if p.forumId == forum.id and p.number == post_number), None)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    return post


@posts_router.post(
    "/forums/{slug}/posts",
    summary="Create new post",
    description="Create a new post in a forum. The post will be assigned the next sequential number.",
    operation_id="createForumPost",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Post created successfully"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        404: {"model": ErrorResponse, "description": "Forum not found"},
    },
)
def create_post(slug: str, post_data: CreatePostRequest, current_user: CurrentUserDep) -> Post:
    """Create new post"""
    forum = next((f for f in mock_forums if f.slug == slug), None)
    if forum is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Forum not found",
        )

    forum_posts = [p for p in mock_posts if p.forumId == forum.id]
    next_number = max([p.number for p in forum_posts], default=0) + 1

    new_post = Post(
        id=str(uuid.uuid4()),
        forumId=forum.id,
        number=next_number,
        title=post_data.title,
        content=post_data.content,
        tags=post_data.tags,
        authorId=current_user.id,
        createdAt=datetime.now(UTC),
        updatedAt=None,
    )
    mock_posts.append(new_post)
    return new_post


@comments_router.get(
    "/forums/{slug}/posts/{post_number}/comments",
    summary="List post comments",
    description="Get all comments for a specific post, sorted by creation date (newest first).",
    operation_id="listPostComments",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "List of comments"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        404: {"model": ErrorResponse, "description": "Forum or post not found"},
    },
)
def get_comments(slug: str, post_number: int, _current_user: CurrentUserDep) -> list[Comment]:
    """Get all comments for a post"""
    forum = next((f for f in mock_forums if f.slug == slug), None)
    if forum is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Forum not found",
        )

    post = next((p for p in mock_posts if p.forumId == forum.id and p.number == post_number), None)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    post_comments = [c for c in mock_comments if c.postId == post.id]
    post_comments.sort(key=lambda c: c.createdAt, reverse=True)

    return post_comments


@comments_router.post(
    "/forums/{slug}/posts/{post_number}/comments",
    summary="Create new comment",
    description="Create a new comment on a specific post.",
    operation_id="createPostComment",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Comment created successfully"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        404: {"model": ErrorResponse, "description": "Forum or post not found"},
    },
)
def create_comment(slug: str, post_number: int, comment_data: CreateCommentRequest, current_user: CurrentUserDep) -> Comment:
    """Create new comment"""
    forum = next((f for f in mock_forums if f.slug == slug), None)
    if forum is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Forum not found",
        )

    post = next((p for p in mock_posts if p.forumId == forum.id and p.number == post_number), None)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    new_comment = Comment(
        id=str(uuid.uuid4()),
        postId=post.id,
        content=comment_data.content,
        authorId=current_user.id,
        createdAt=datetime.now(UTC),
        updatedAt=None,
    )
    mock_comments.append(new_comment)
    return new_comment


@users_router.get(
    "/users",
    summary="List all users",
    description="Get a list of all users in the system (excluding password information).",
    operation_id="listUsers",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "List of users"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
    },
)
def get_users(_current_user: CurrentUserDep) -> list[User]:
    """Get all users (without passwords)"""
    return [User(id=u.id, username=u.username, role=u.role) for u in mock_users]
