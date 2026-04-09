"""Authentication dependencies for route protection."""

import time

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.user import User

security = HTTPBearer(auto_error=False)

_user_cache: dict[str, tuple[User, float]] = {}
_CACHE_TTL = 60


def _get_cached_user(user_id: str) -> User | None:
    entry = _user_cache.get(user_id)
    if entry and time.monotonic() - entry[1] < _CACHE_TTL:
        return entry[0]
    _user_cache.pop(user_id, None)
    return None


def _set_cached_user(user_id: str, user: User) -> None:
    if len(_user_cache) > 1000:
        now = time.monotonic()
        stale = [k for k, (_, t) in _user_cache.items() if now - t >= _CACHE_TTL]
        for k in stale:
            del _user_cache[k]
    _user_cache[user_id] = (user, time.monotonic())


def _extract_token(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None,
) -> str:
    """Extract JWT from Bearer header (mobile) or httpOnly cookie (web)."""
    if credentials and credentials.credentials:
        return credentials.credentials

    token = request.cookies.get("token")
    if token:
        return token

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
    )


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Decode JWT from cookie or Bearer header and return the authenticated User."""
    token = _extract_token(request, credentials)
    try:
        payload = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing subject",
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    cached = _get_cached_user(user_id)
    if cached is not None:
        return cached

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    _set_cached_user(user_id, user)
    return user


async def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user
