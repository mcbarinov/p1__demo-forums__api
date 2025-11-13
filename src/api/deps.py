from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyCookie, HTTPAuthorizationCredentials, HTTPBearer

from .data import sessions
from .models import User

# Security schemes
bearer_scheme = HTTPBearer(auto_error=False)
cookie_scheme = APIKeyCookie(name="session_id", auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)] = None,
    session_cookie: Annotated[str | None, Depends(cookie_scheme)] = None,
) -> User:
    """Get and validate current user from Authorization Bearer header or session cookie."""

    # Check Bearer token first (preferred)
    if credentials and credentials.scheme == "Bearer":
        token = credentials.credentials
        user = sessions.get(token)
        if user:
            return user

    # Fallback to cookie-based session
    if session_cookie:
        user = sessions.get(session_cookie)
        if user:
            return user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
    )


# Type alias for dependency
CurrentUserDep = Annotated[User, Depends(get_current_user)]
