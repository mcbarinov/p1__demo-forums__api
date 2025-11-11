from typing import Annotated

from fastapi import Depends, HTTPException, Request, status

from .data import sessions
from .models import User


def validate_session(request: Request) -> User | None:
    """Validate session from Bearer token (priority) or HttpOnly cookie (fallback)"""
    # Priority 1: Check Authorization header for Bearer token
    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[7:]  # Strip "Bearer " prefix
        user = sessions.get(token)
        if user:
            return user

    # Priority 2: Fall back to cookie-based session
    session_id = request.cookies.get("session_id")
    if session_id:
        return sessions.get(session_id)

    return None


def get_current_user(request: Request) -> User:
    """Dependency to get current authenticated user"""
    user = validate_session(request)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
