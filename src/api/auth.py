from typing import Annotated

from fastapi import Depends, HTTPException, Request, status

from .data import sessions
from .models import User


def validate_session(request: Request) -> User | None:
    """Validate session from Authorization header"""
    auth_header = request.headers.get("authorization")
    if not auth_header:
        return None

    if not auth_header.startswith("Bearer "):
        return None

    token = auth_header[7:]
    return sessions.get(token)


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
