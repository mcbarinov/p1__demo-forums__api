import math
import os
import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, Response, status

from .auth import CurrentUser
from .data import (
    mock_comments,
    mock_forums,
    mock_posts,
    mock_users,
    sessions,
)
from .models import (
    ChangePasswordRequest,
    Comment,
    CreateCommentRequest,
    CreateForumRequest,
    CreatePostRequest,
    Forum,
    LoginRequest,
    LoginResponse,
    MessageResponse,
    PaginatedResponse,
    Post,
    User,
)

router = APIRouter()

# Secure flag for cookies: True in production, False in development
# In production, reverse proxy (Caddy/Nginx) terminates SSL
SECURE_COOKIES = os.getenv("ENVIRONMENT", "development") == "production"


@router.post("/api/auth/login", status_code=status.HTTP_200_OK)
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


@router.post("/api/auth/logout", status_code=status.HTTP_200_OK)
def logout(current_user: CurrentUser, response: Response) -> MessageResponse:
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


@router.get("/api/profile", status_code=status.HTTP_200_OK)
def get_profile(current_user: CurrentUser) -> User:
    """Get current user profile"""
    return current_user


@router.post("/api/profile/change-password", status_code=status.HTTP_200_OK)
def change_password(request: ChangePasswordRequest, current_user: CurrentUser) -> MessageResponse:
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


@router.get("/api/forums", status_code=status.HTTP_200_OK)
def get_forums(_current_user: CurrentUser) -> list[Forum]:
    """Get all forums"""
    return mock_forums


@router.post("/api/forums", status_code=status.HTTP_201_CREATED)
def create_forum(forum_data: CreateForumRequest, _current_user: CurrentUser) -> Forum:
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


@router.get("/api/forums/{slug}/posts", status_code=status.HTTP_200_OK)
def get_posts(slug: str, _current_user: CurrentUser, page: int = 1, page_size: int = 10) -> PaginatedResponse[Post]:
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
        totalCount=total_count,
        page=page,
        pageSize=page_size,
        totalPages=total_pages,
    )


@router.get("/api/forums/{slug}/posts/{post_number}", status_code=status.HTTP_200_OK)
def get_post(slug: str, post_number: int, _current_user: CurrentUser) -> Post:
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


@router.post("/api/forums/{slug}/posts", status_code=status.HTTP_201_CREATED)
def create_post(slug: str, post_data: CreatePostRequest, current_user: CurrentUser) -> Post:
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


@router.get("/api/forums/{slug}/posts/{post_number}/comments", status_code=status.HTTP_200_OK)
def get_comments(slug: str, post_number: int, _current_user: CurrentUser) -> list[Comment]:
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


@router.post("/api/forums/{slug}/posts/{post_number}/comments", status_code=status.HTTP_201_CREATED)
def create_comment(slug: str, post_number: int, comment_data: CreateCommentRequest, current_user: CurrentUser) -> Comment:
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


@router.get("/api/users", status_code=status.HTTP_200_OK)
def get_users(_current_user: CurrentUser) -> list[User]:
    """Get all users (without passwords)"""
    return [User(id=u.id, username=u.username, role=u.role) for u in mock_users]
