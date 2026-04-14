# Production Authentication Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace all mock/prototype auth with production-grade OTP authentication using httpOnly cookies (web), Bearer tokens (mobile), CSRF protection, and Sarvam AI SMS delivery.

**Architecture:** Three-layer approach — (1) API backend with OTP provider abstraction, bcrypt-hashed OTP storage, cookie-based JWT issuance, and CSRF middleware, (2) Admin Next.js login page with cookie-based auth, (3) Mobile Expo login with Bearer token auth. Both clients share the same API endpoints with client-type differentiation.

**Tech Stack:** FastAPI + SQLAlchemy (API), Next.js + Refine + MUI (Admin), Expo + React Native Paper (Mobile), PostgreSQL (DB), bcrypt (OTP hashing), python-jose (JWT), Sarvam AI (SMS)

**Design Doc:** `docs/plans/2026-04-09-production-auth-design.md`

---

## Task 1: OTP Model and Migration

**Files:**
- Create: `packages/api/app/models/otp.py`
- Modify: `packages/api/alembic/env.py` (ensure model imported)
- Create: `packages/api/alembic/versions/add_otp_requests_table.py`

**Step 1: Create OTPRequest SQLAlchemy model**

Create `packages/api/app/models/otp.py`:

```python
from datetime import datetime

from sqlalchemy import String, Integer, DateTime, Index, text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class OTPRequest(Base):
    __tablename__ = "otp_requests"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    phone: Mapped[str] = mapped_column(String(15), unique=True, nullable=False)
    otp_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_otp_expires", "expires_at"),
    )
```

**Step 2: Generate Alembic migration**

Run from `packages/api/`:

```bash
cd packages/api && alembic revision --autogenerate -m "add otp_requests table"
```

Review the generated migration — it should create the `otp_requests` table with the UUID PK, unique constraint on `phone`, and index on `expires_at`.

**Step 3: Apply migration**

```bash
cd packages/api && alembic upgrade head
```

Expected: Table `otp_requests` created in PostgreSQL.

**Step 4: Verify**

```bash
docker compose exec db psql -U pashu -d pashuraksha -c "\d otp_requests"
```

Expected: Table with columns `id`, `phone`, `otp_hash`, `attempts`, `expires_at`, `created_at`.

**Step 5: Commit**

```bash
git add packages/api/app/models/otp.py packages/api/alembic/versions/*otp*
git commit -m "feat(api): add otp_requests model and migration"
```

---

## Task 2: OTP Provider Abstraction

**Files:**
- Create: `packages/api/app/services/otp/__init__.py`
- Create: `packages/api/app/services/otp/base.py`
- Create: `packages/api/app/services/otp/console.py`
- Create: `packages/api/app/services/otp/sarvam.py`

**Step 1: Create abstract base provider**

Create `packages/api/app/services/otp/base.py`:

```python
from abc import ABC, abstractmethod


class OTPProvider(ABC):
    @abstractmethod
    async def send_otp(self, phone: str, otp: str) -> None:
        """Deliver an OTP to the given phone number.

        Raises:
            RuntimeError: If delivery fails.
        """
```

**Step 2: Create console provider (development)**

Create `packages/api/app/services/otp/console.py`:

```python
import logging

from app.services.otp.base import OTPProvider

logger = logging.getLogger("pashuraksha.otp")


class ConsoleOTPProvider(OTPProvider):
    async def send_otp(self, phone: str, otp: str) -> None:
        logger.info(
            "\n"
            "╔══════════════════════════════════╗\n"
            "║  DEV OTP for %-15s   ║\n"
            "║  Code: %s                     ║\n"
            "╚══════════════════════════════════╝",
            phone,
            otp,
        )
```

**Step 3: Create Sarvam AI provider (production)**

Create `packages/api/app/services/otp/sarvam.py`:

```python
import httpx

from app.services.otp.base import OTPProvider


class SarvamOTPProvider(OTPProvider):
    def __init__(self, api_key: str) -> None:
        self._api_key = api_key
        self._base_url = "https://api.sarvam.ai"

    async def send_otp(self, phone: str, otp: str) -> None:
        message = f"Your PashuRaksha verification code is {otp}. Valid for 5 minutes. Do not share."
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                f"{self._base_url}/v1/sms/send",
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
                json={"phone": phone, "message": message},
            )
            if resp.status_code >= 400:
                raise RuntimeError(
                    f"Sarvam SMS failed ({resp.status_code}): {resp.text}"
                )
```

Note: The Sarvam AI SMS endpoint URL and payload may need adjustment based on their actual API docs. This is the expected shape — verify against https://docs.sarvam.ai before deploying.

**Step 4: Create provider factory**

Create `packages/api/app/services/otp/__init__.py`:

```python
from app.config import settings
from app.services.otp.base import OTPProvider


def get_otp_provider() -> OTPProvider:
    if settings.environment == "development":
        from app.services.otp.console import ConsoleOTPProvider
        return ConsoleOTPProvider()
    else:
        from app.services.otp.sarvam import SarvamOTPProvider
        if not settings.sarvam_api_key:
            raise RuntimeError("SARVAM_API_KEY is required in non-development environments")
        return SarvamOTPProvider(settings.sarvam_api_key)
```

**Step 5: Commit**

```bash
git add packages/api/app/services/otp/
git commit -m "feat(api): add OTP provider abstraction with Sarvam and console backends"
```

---

## Task 3: Update Auth Schemas

**Files:**
- Modify: `packages/api/app/schemas/auth.py`

**Step 1: Update schemas with new fields and error codes**

Replace `packages/api/app/schemas/auth.py` entirely:

```python
from enum import Enum

from pydantic import BaseModel, Field


class OTPRequest(BaseModel):
    phone: str = Field(..., pattern=r"^\+91[6-9]\d{9}$", examples=["+919876543210"])


class OTPVerify(BaseModel):
    phone: str = Field(..., pattern=r"^\+91[6-9]\d{9}$")
    otp: str = Field(..., min_length=6, max_length=6, examples=["123456"])
    remember_me: bool = False
    client_type: str = Field(default="web", pattern=r"^(web|mobile)$")


class AuthUserResponse(BaseModel):
    """Response body for verify-otp and /me endpoints."""
    user_id: str
    role: str
    name: str | None = None


class TokenResponse(AuthUserResponse):
    """Extended response for mobile clients that receive token in body."""
    access_token: str
    token_type: str = "bearer"


class AuthErrorCode(str, Enum):
    OTP_EXPIRED = "OTP_EXPIRED"
    OTP_INVALID = "OTP_INVALID"
    OTP_MAX_ATTEMPTS = "OTP_MAX_ATTEMPTS"
    RATE_LIMITED = "RATE_LIMITED"
    ROLE_NOT_AUTHORIZED = "ROLE_NOT_AUTHORIZED"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    TOKEN_INVALID = "TOKEN_INVALID"


class AuthErrorResponse(BaseModel):
    detail: str
    code: AuthErrorCode
```

**Step 2: Commit**

```bash
git add packages/api/app/schemas/auth.py
git commit -m "feat(api): update auth schemas with remember_me, client_type, error codes"
```

---

## Task 4: Rewrite Auth Router

**Files:**
- Modify: `packages/api/app/routers/auth.py` (full rewrite)

**Step 1: Rewrite auth router**

Replace `packages/api/app/routers/auth.py` entirely:

```python
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from jose import jwt
from passlib.hash import bcrypt
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.otp import OTPRequest as OTPRequestModel
from app.models.user import User
from app.schemas.auth import (
    AuthErrorCode,
    AuthUserResponse,
    OTPRequest,
    OTPVerify,
    TokenResponse,
)
from app.services.otp import get_otp_provider

router = APIRouter(prefix="/v1/auth", tags=["auth"])

_otp_provider = None

STAFF_ROLES = {"admin", "vet", "milk_center"}

# Session durations
DEFAULT_EXPIRY = timedelta(hours=8)
REMEMBER_EXPIRY = timedelta(days=7)

# Rate limits
MAX_OTP_REQUESTS_PER_HOUR = 5
MAX_OTP_ATTEMPTS = 3
OTP_EXPIRY_MINUTES = 5


def _get_provider():
    global _otp_provider
    if _otp_provider is None:
        _otp_provider = get_otp_provider()
    return _otp_provider


def _auth_error(status_code: int, code: AuthErrorCode, detail: str):
    return HTTPException(
        status_code=status_code,
        detail={"detail": detail, "code": code.value},
    )


def _generate_otp() -> str:
    return str(secrets.randbelow(900000) + 100000)


def _set_auth_cookies(response: Response, token: str, csrf_token: str, max_age: int):
    secure = settings.environment != "development"
    response.set_cookie(
        key="token",
        value=token,
        httponly=True,
        secure=secure,
        samesite="lax",
        max_age=max_age,
        path="/",
    )
    response.set_cookie(
        key="csrf_token",
        value=csrf_token,
        httponly=False,
        secure=secure,
        samesite="lax",
        max_age=max_age,
        path="/",
    )


def _clear_auth_cookies(response: Response):
    response.delete_cookie("token", path="/")
    response.delete_cookie("csrf_token", path="/")


@router.post("/request-otp")
async def request_otp(body: OTPRequest, db: AsyncSession = Depends(get_db)):
    # Rate limit: max requests per phone per hour
    one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
    result = await db.execute(
        select(OTPRequestModel).where(
            OTPRequestModel.phone == body.phone,
            OTPRequestModel.created_at > one_hour_ago,
        )
    )
    recent = result.scalars().all()
    if len(recent) >= MAX_OTP_REQUESTS_PER_HOUR:
        raise _auth_error(
            status.HTTP_429_TOO_MANY_REQUESTS,
            AuthErrorCode.RATE_LIMITED,
            "Too many OTP requests. Try again later.",
        )

    # Delete any existing OTP for this phone
    await db.execute(
        delete(OTPRequestModel).where(OTPRequestModel.phone == body.phone)
    )

    # Generate, hash, and store new OTP
    otp = _generate_otp()
    otp_hash = bcrypt.hash(otp)
    otp_record = OTPRequestModel(
        phone=body.phone,
        otp_hash=otp_hash,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=OTP_EXPIRY_MINUTES),
    )
    db.add(otp_record)
    await db.commit()

    # Deliver OTP via provider
    provider = _get_provider()
    await provider.send_otp(body.phone, otp)

    return {"message": "OTP sent successfully"}


@router.post("/verify-otp")
async def verify_otp(body: OTPVerify, db: AsyncSession = Depends(get_db)):
    # Look up OTP record
    result = await db.execute(
        select(OTPRequestModel).where(OTPRequestModel.phone == body.phone)
    )
    otp_record = result.scalar_one_or_none()

    if not otp_record:
        raise _auth_error(
            status.HTTP_401_UNAUTHORIZED,
            AuthErrorCode.OTP_INVALID,
            "No OTP request found. Please request a new OTP.",
        )

    # Check expiry
    if datetime.now(timezone.utc) > otp_record.expires_at:
        await db.execute(
            delete(OTPRequestModel).where(OTPRequestModel.phone == body.phone)
        )
        await db.commit()
        raise _auth_error(
            status.HTTP_401_UNAUTHORIZED,
            AuthErrorCode.OTP_EXPIRED,
            "OTP has expired. Please request a new one.",
        )

    # Check max attempts
    if otp_record.attempts >= MAX_OTP_ATTEMPTS:
        await db.execute(
            delete(OTPRequestModel).where(OTPRequestModel.phone == body.phone)
        )
        await db.commit()
        raise _auth_error(
            status.HTTP_401_UNAUTHORIZED,
            AuthErrorCode.OTP_MAX_ATTEMPTS,
            "Too many failed attempts. Please request a new OTP.",
        )

    # Verify OTP hash
    if not bcrypt.verify(body.otp, otp_record.otp_hash):
        otp_record.attempts += 1
        await db.commit()
        raise _auth_error(
            status.HTTP_401_UNAUTHORIZED,
            AuthErrorCode.OTP_INVALID,
            "Invalid OTP. Please try again.",
        )

    # OTP is valid — delete it (one-time use)
    await db.execute(
        delete(OTPRequestModel).where(OTPRequestModel.phone == body.phone)
    )

    # Find or create user
    user_result = await db.execute(select(User).where(User.phone == body.phone))
    user = user_result.scalar_one_or_none()

    if not user:
        user = User(
            phone=body.phone,
            name=f"Farmer {body.phone[-4:]}",
            role="farmer",
            lang_pref="kn",
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    # Role gate for web clients
    if body.client_type == "web" and user.role not in STAFF_ROLES:
        raise _auth_error(
            status.HTTP_403_FORBIDDEN,
            AuthErrorCode.ROLE_NOT_AUTHORIZED,
            "This portal is for staff. Please use the PashuRaksha mobile app.",
        )

    # Generate JWT
    expiry = REMEMBER_EXPIRY if body.remember_me else DEFAULT_EXPIRY
    max_age_seconds = int(expiry.total_seconds())
    token_data = {
        "sub": str(user.id),
        "role": user.role,
        "phone": user.phone,
        "exp": datetime.now(timezone.utc) + expiry,
    }
    access_token = jwt.encode(token_data, settings.jwt_secret, algorithm=settings.jwt_algorithm)

    # Generate CSRF token
    csrf_token = secrets.token_urlsafe(32)

    # Mobile: return token in body
    if body.client_type == "mobile":
        return TokenResponse(
            access_token=access_token,
            user_id=str(user.id),
            role=user.role,
            name=user.name,
        )

    # Web: set httpOnly cookies, return user info only
    response = JSONResponse(
        content=AuthUserResponse(
            user_id=str(user.id),
            role=user.role,
            name=user.name,
        ).model_dump()
    )
    _set_auth_cookies(response, access_token, csrf_token, max_age_seconds)
    return response


@router.get("/me", response_model=AuthUserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return AuthUserResponse(
        user_id=str(current_user.id),
        role=current_user.role,
        name=current_user.name,
    )


@router.post("/logout")
async def logout():
    response = JSONResponse(content={"message": "Logged out"})
    _clear_auth_cookies(response)
    return response
```

**Step 2: Commit**

```bash
git add packages/api/app/routers/auth.py
git commit -m "feat(api): rewrite auth router with real OTP flow, cookies, and role gate"
```

---

## Task 5: Update Auth Middleware for Cookie Support

**Files:**
- Modify: `packages/api/app/middleware/auth.py`

**Step 1: Update get_current_user to read from both cookies and Bearer header**

Replace `packages/api/app/middleware/auth.py` entirely:

```python
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
```

**Step 2: Commit**

```bash
git add packages/api/app/middleware/auth.py
git commit -m "feat(api): update auth middleware to support both cookies and Bearer tokens"
```

---

## Task 6: CSRF Middleware

**Files:**
- Create: `packages/api/app/middleware/csrf.py`
- Modify: `packages/api/app/main.py`

**Step 1: Create CSRF middleware**

Create `packages/api/app/middleware/csrf.py`:

```python
"""Double-submit cookie CSRF protection middleware."""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

EXEMPT_PATHS = {
    "/v1/auth/request-otp",
    "/v1/auth/verify-otp",
    "/v1/auth/logout",
    "/health",
}

MUTATING_METHODS = {"POST", "PUT", "DELETE", "PATCH"}


class CSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method not in MUTATING_METHODS:
            return await call_next(request)

        if request.url.path in EXEMPT_PATHS:
            return await call_next(request)

        # Skip CSRF check for mobile clients using Bearer auth
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            return await call_next(request)

        # Double-submit check: compare cookie vs header
        cookie_token = request.cookies.get("csrf_token")
        header_token = request.headers.get("x-csrf-token")

        if not cookie_token or not header_token:
            return JSONResponse(
                status_code=403,
                content={"detail": "CSRF token missing", "code": "CSRF_MISSING"},
            )

        if cookie_token != header_token:
            return JSONResponse(
                status_code=403,
                content={"detail": "CSRF token mismatch", "code": "CSRF_MISMATCH"},
            )

        return await call_next(request)
```

**Step 2: Update main.py — add CSRF middleware, fix CORS, add startup validation**

Replace `packages/api/app/main.py` entirely:

```python
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.config import settings
from app.database import engine, get_db
from app.middleware.csrf import CSRFMiddleware

logger = logging.getLogger(__name__)

from app.routers import (
    auth,
    animals,
    health,
    milk,
    finance,
    shg,
    schemes,
    marketplace,
    income,
    admin,
    weather,
    feed,
    ethno_vet,
    bharat_pashudhan,
    vaccination,
    insurance,
    alerts,
    medicine,
    medicine_log,
    milk_center,
    advisory,
    onboarding,
    iot,
    map_points,
    users,
)


def _validate_settings():
    """Fail fast if required settings are missing or insecure."""
    if not settings.database_url:
        raise RuntimeError("DATABASE_URL is required")
    if not settings.jwt_secret:
        raise RuntimeError("JWT_SECRET is required")
    if len(settings.jwt_secret) < 32:
        raise RuntimeError(
            "JWT_SECRET must be at least 32 characters (256 bits). "
            "Generate with: openssl rand -hex 32"
        )
    if settings.environment != "development" and not settings.sarvam_api_key:
        raise RuntimeError("SARVAM_API_KEY is required in non-development environments")
    if settings.environment != "development" and not settings.cors_origins:
        raise RuntimeError("CORS_ORIGINS is required in non-development environments")


@asynccontextmanager
async def lifespan(app: FastAPI):
    _validate_settings()
    yield
    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title="PashuRaksha ERP",
        description="Livestock management ERP for rural Indian farmers",
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS — read from settings, not hardcoded
    origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
        allow_headers=["Authorization", "Content-Type", "X-CSRF-Token"],
    )

    # CSRF middleware (must be added after CORS)
    app.add_middleware(CSRFMiddleware)

    # --- Routers ---
    app.include_router(auth.router)
    app.include_router(animals.router)
    app.include_router(health.router)
    app.include_router(milk.router)
    app.include_router(finance.router)
    app.include_router(shg.router)
    app.include_router(schemes.router)
    app.include_router(marketplace.router)
    app.include_router(income.router)
    app.include_router(admin.router)
    app.include_router(weather.router)
    app.include_router(feed.router)
    app.include_router(ethno_vet.router)
    app.include_router(bharat_pashudhan.router)
    app.include_router(vaccination.router)
    app.include_router(insurance.router)
    app.include_router(alerts.router)
    app.include_router(medicine.router)
    app.include_router(medicine_log.router)
    app.include_router(milk_center.router)
    app.include_router(advisory.router)
    app.include_router(onboarding.router)
    app.include_router(iot.router)
    app.include_router(map_points.router)
    app.include_router(users.router)

    @app.get("/health")
    async def healthcheck():
        try:
            async for session in get_db():
                await session.execute(text("SELECT 1"))
            return {"status": "healthy", "database": "connected"}
        except Exception:
            logger.exception("Health check failed")
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=503,
                content={"status": "unhealthy", "database": "disconnected"},
            )

    return app


app = create_app()
```

**Step 3: Commit**

```bash
git add packages/api/app/middleware/csrf.py packages/api/app/main.py
git commit -m "feat(api): add CSRF middleware, CORS from env, startup validation"
```

---

## Task 7: Update API Config with Validation

**Files:**
- Modify: `packages/api/app/config.py`
- Modify: `packages/api/.env` (update JWT secret)

**Step 1: Generate a strong JWT secret**

```bash
openssl rand -hex 32
```

Copy the output (64 hex characters).

**Step 2: Update .env with strong secret**

Update `packages/api/.env` — replace the existing `JWT_SECRET` with the generated value. Also ensure `ENVIRONMENT=development` is set explicitly.

Example (DO NOT use this exact value):

```
DATABASE_URL=postgresql+asyncpg://pashu:pashu_dev_2026@localhost:5432/pashuraksha
JWT_SECRET=<paste-64-char-hex-from-step-1>
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3000,http://localhost:8081,http://localhost:19006
```

**Step 3: Commit**

```bash
git add packages/api/app/config.py
git commit -m "feat(api): strengthen config validation"
```

Note: Do NOT commit `.env` — ensure it's in `.gitignore`.

---

## Task 8: Update Test Fixtures

**Files:**
- Modify: `packages/api/tests/conftest.py`

**Step 1: Update conftest to work with new auth flow**

Replace `packages/api/tests/conftest.py`:

```python
"""Shared fixtures for PashuRaksha API tests.

Tests run against a live local API (environment=development).
The console OTP provider logs OTPs to stdout — tests extract them
by calling request-otp then verify-otp with the known dev OTP.

For simplicity in integration tests, we use a helper that calls
both endpoints to get a valid token.
"""

import httpx
import pytest

BASE_URL = "http://localhost:8000"

FARMER_PHONE = "+919900000002"
ADMIN_PHONE = "+919900000001"


def _get_token(phone: str) -> str:
    """Request OTP then verify with known dev OTP extracted from console."""
    # Step 1: Request OTP (in dev mode, OTP is logged to console)
    r = httpx.post(f"{BASE_URL}/v1/auth/request-otp", json={"phone": phone})
    assert r.status_code == 200, f"OTP request failed: {r.text}"

    # Step 2: In dev, we need to read the OTP from the database directly
    # or use a test-only endpoint. For integration tests against live API,
    # we verify with the OTP from the database.
    # Alternative: test with a predictable OTP seeded via test helper.
    #
    # For now, use the verify endpoint with client_type=mobile to get token in body.
    # The actual OTP must be obtained from the API logs in dev mode.
    # In CI, set TEST_OTP env var or use a test helper endpoint.
    import os
    test_otp = os.environ.get("TEST_OTP", "")
    if not test_otp:
        pytest.skip("TEST_OTP env var required for auth tests")

    r = httpx.post(
        f"{BASE_URL}/v1/auth/verify-otp",
        json={"phone": phone, "otp": test_otp, "client_type": "mobile"},
    )
    assert r.status_code == 200, f"Auth failed: {r.text}"
    return r.json()["access_token"]


@pytest.fixture(scope="session")
def base_url() -> str:
    return BASE_URL


@pytest.fixture(scope="session")
def farmer_token() -> str:
    return _get_token(FARMER_PHONE)


@pytest.fixture(scope="session")
def admin_token() -> str:
    return _get_token(ADMIN_PHONE)


@pytest.fixture(scope="session")
def farmer_user_id() -> str:
    r = httpx.post(
        f"{BASE_URL}/v1/auth/verify-otp",
        json={"phone": FARMER_PHONE, "otp": "", "client_type": "mobile"},
    )
    if r.status_code == 200:
        return r.json()["user_id"]
    pytest.skip("Could not get farmer user_id")


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}
```

Note: Integration tests now require the API to be running with `ENVIRONMENT=development`. The test setup needs the OTP from the console log. For CI, add a test-only endpoint or seed predictable OTPs.

**Step 2: Commit**

```bash
git add packages/api/tests/conftest.py
git commit -m "feat(api): update test fixtures for new auth flow"
```

---

## Task 9: Admin Login Page

**Files:**
- Create: `packages/admin/src/app/login/page.tsx`

**Step 1: Create the login page**

Create `packages/admin/src/app/login/page.tsx`:

```tsx
"use client";

import React, { useState, useRef, useEffect, useCallback } from "react";
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  InputAdornment,
  Checkbox,
  FormControlLabel,
  Alert,
  Link,
  CircularProgress,
} from "@mui/material";
import PhoneIcon from "@mui/icons-material/Phone";

const API_URL = process.env.NEXT_PUBLIC_API_URL;

const PHONE_REGEX = /^[6-9]\d{9}$/;
const OTP_LENGTH = 6;
const RESEND_COOLDOWN_SECONDS = 60;

interface AuthError {
  detail: string;
  code: string;
}

export default function LoginPage() {
  const [step, setStep] = useState<"phone" | "otp">("phone");
  const [phone, setPhone] = useState("");
  const [otp, setOtp] = useState(Array(OTP_LENGTH).fill(""));
  const [rememberMe, setRememberMe] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [resendCooldown, setResendCooldown] = useState(0);

  const otpRefs = useRef<(HTMLInputElement | null)[]>([]);

  // Resend cooldown timer
  useEffect(() => {
    if (resendCooldown <= 0) return;
    const timer = setInterval(() => setResendCooldown((c) => c - 1), 1000);
    return () => clearInterval(timer);
  }, [resendCooldown]);

  const phoneWithPrefix = `+91${phone}`;
  const isPhoneValid = PHONE_REGEX.test(phone);
  const otpString = otp.join("");
  const isOtpComplete = otpString.length === OTP_LENGTH;

  const handleSendOtp = useCallback(async () => {
    if (!isPhoneValid) return;
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`${API_URL}/auth/request-otp`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ phone: phoneWithPrefix }),
        credentials: "include",
      });
      if (!res.ok) {
        const err: AuthError = await res.json();
        throw new Error(err.detail || "Failed to send OTP");
      }
      setStep("otp");
      setResendCooldown(RESEND_COOLDOWN_SECONDS);
      setTimeout(() => otpRefs.current[0]?.focus(), 100);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Network error");
    } finally {
      setLoading(false);
    }
  }, [isPhoneValid, phoneWithPrefix]);

  const handleVerifyOtp = useCallback(async () => {
    if (!isOtpComplete) return;
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`${API_URL}/auth/verify-otp`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          phone: phoneWithPrefix,
          otp: otpString,
          remember_me: rememberMe,
          client_type: "web",
        }),
        credentials: "include",
      });
      if (!res.ok) {
        const err: AuthError = await res.json();
        setError(err.detail || "Verification failed");
        if (err.code === "OTP_MAX_ATTEMPTS" || err.code === "OTP_EXPIRED") {
          setStep("phone");
          setOtp(Array(OTP_LENGTH).fill(""));
        }
        return;
      }
      // Cookies set by server — redirect to dashboard
      window.location.href = "/";
    } catch (e) {
      setError(e instanceof Error ? e.message : "Network error");
    } finally {
      setLoading(false);
    }
  }, [isOtpComplete, phoneWithPrefix, otpString, rememberMe]);

  const handleOtpChange = (value: string, index: number) => {
    // Handle paste
    if (value.length > 1) {
      const digits = value.replace(/\D/g, "").slice(0, OTP_LENGTH).split("");
      const newOtp = [...otp];
      digits.forEach((d, i) => {
        if (index + i < OTP_LENGTH) newOtp[index + i] = d;
      });
      setOtp(newOtp);
      const focusIdx = Math.min(index + digits.length, OTP_LENGTH - 1);
      otpRefs.current[focusIdx]?.focus();
      return;
    }

    const newOtp = [...otp];
    newOtp[index] = value.replace(/\D/g, "");
    setOtp(newOtp);
    if (value && index < OTP_LENGTH - 1) {
      otpRefs.current[index + 1]?.focus();
    }
  };

  const handleOtpKeyDown = (e: React.KeyboardEvent, index: number) => {
    if (e.key === "Backspace" && !otp[index] && index > 0) {
      otpRefs.current[index - 1]?.focus();
    }
  };

  const handleResend = () => {
    setOtp(Array(OTP_LENGTH).fill(""));
    setError("");
    handleSendOtp();
  };

  const handleChangePhone = () => {
    setStep("phone");
    setOtp(Array(OTP_LENGTH).fill(""));
    setError("");
  };

  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        bgcolor: "#f0f4f3",
        p: 2,
      }}
    >
      <Card sx={{ maxWidth: 440, width: "100%", borderRadius: 3, boxShadow: 3 }}>
        {/* Header */}
        <Box
          sx={{
            bgcolor: "#0f6b42",
            color: "#fff",
            textAlign: "center",
            py: 4,
            borderRadius: "12px 12px 0 0",
          }}
        >
          <Typography variant="h3" sx={{ mb: 0.5 }}>
            {"\uD83D\uDC04"}
          </Typography>
          <Typography variant="h5" fontWeight={700}>
            PashuRaksha
          </Typography>
          <Typography variant="body2" sx={{ color: "#a8f5c8", mt: 0.5 }}>
            Admin Portal
          </Typography>
        </Box>

        <CardContent sx={{ p: 4 }}>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError("")}>
              {error}
            </Alert>
          )}

          {step === "phone" ? (
            <>
              <Typography variant="h6" fontWeight={700} sx={{ mb: 2 }}>
                Staff Login
              </Typography>
              <TextField
                fullWidth
                label="Mobile Number"
                placeholder="9876543210"
                value={phone}
                onChange={(e) => setPhone(e.target.value.replace(/\D/g, "").slice(0, 10))}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <PhoneIcon sx={{ mr: 0.5 }} />
                      +91
                    </InputAdornment>
                  ),
                }}
                inputProps={{ inputMode: "numeric", maxLength: 10 }}
                error={phone.length === 10 && !isPhoneValid}
                helperText={
                  phone.length === 10 && !isPhoneValid
                    ? "Enter a valid Indian mobile number"
                    : " "
                }
                sx={{ mb: 2 }}
              />
              <Button
                fullWidth
                variant="contained"
                size="large"
                onClick={handleSendOtp}
                disabled={!isPhoneValid || loading}
                sx={{
                  bgcolor: "#0f6b42",
                  "&:hover": { bgcolor: "#0a5534" },
                  textTransform: "none",
                  fontWeight: 700,
                  fontSize: 16,
                  py: 1.5,
                  borderRadius: 2,
                }}
              >
                {loading ? <CircularProgress size={24} color="inherit" /> : "Send OTP"}
              </Button>
            </>
          ) : (
            <>
              <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                <Typography variant="body1" sx={{ mr: 1 }}>
                  OTP sent to +91 {phone}
                </Typography>
                <Link
                  component="button"
                  variant="body2"
                  onClick={handleChangePhone}
                  sx={{ color: "#0f6b42" }}
                >
                  Change
                </Link>
              </Box>

              {/* OTP boxes */}
              <Box sx={{ display: "flex", gap: 1, mb: 2, justifyContent: "center" }}>
                {otp.map((digit, i) => (
                  <TextField
                    key={i}
                    inputRef={(el) => { otpRefs.current[i] = el; }}
                    value={digit}
                    onChange={(e) => handleOtpChange(e.target.value, i)}
                    onKeyDown={(e) => handleOtpKeyDown(e, i)}
                    inputProps={{
                      maxLength: i === 0 ? OTP_LENGTH : 1,
                      style: { textAlign: "center", fontSize: 24, fontWeight: 700, padding: "12px 0" },
                      inputMode: "numeric",
                      "aria-label": `OTP digit ${i + 1} of ${OTP_LENGTH}`,
                    }}
                    sx={{ width: 52 }}
                  />
                ))}
              </Box>

              <FormControlLabel
                control={
                  <Checkbox
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                    sx={{ color: "#0f6b42", "&.Mui-checked": { color: "#0f6b42" } }}
                  />
                }
                label="Remember this device (7 days)"
                sx={{ mb: 2, display: "block" }}
              />

              <Button
                fullWidth
                variant="contained"
                size="large"
                onClick={handleVerifyOtp}
                disabled={!isOtpComplete || loading}
                sx={{
                  bgcolor: "#0f6b42",
                  "&:hover": { bgcolor: "#0a5534" },
                  textTransform: "none",
                  fontWeight: 700,
                  fontSize: 16,
                  py: 1.5,
                  borderRadius: 2,
                  mb: 1.5,
                }}
              >
                {loading ? <CircularProgress size={24} color="inherit" /> : "Verify & Login"}
              </Button>

              <Box sx={{ textAlign: "center" }}>
                {resendCooldown > 0 ? (
                  <Typography variant="body2" color="text.secondary">
                    Resend OTP in {resendCooldown}s
                  </Typography>
                ) : (
                  <Link
                    component="button"
                    variant="body2"
                    onClick={handleResend}
                    disabled={loading}
                    sx={{ color: "#0f6b42" }}
                  >
                    Resend OTP
                  </Link>
                )}
              </Box>
            </>
          )}
        </CardContent>
      </Card>
    </Box>
  );
}
```

**Step 2: Commit**

```bash
git add packages/admin/src/app/login/page.tsx
git commit -m "feat(admin): add production login page with phone + OTP + remember me"
```

---

## Task 10: Update Admin Auth Provider (Cookie-Based)

**Files:**
- Modify: `packages/admin/src/providers/auth-provider.ts`

**Step 1: Rewrite auth provider for httpOnly cookies**

Replace `packages/admin/src/providers/auth-provider.ts` entirely:

```typescript
import type { AuthProvider } from "@refinedev/core";

const API_URL = process.env.NEXT_PUBLIC_API_URL;
if (!API_URL) {
  throw new Error("NEXT_PUBLIC_API_URL environment variable is required");
}

// In-memory cache for the current session (not localStorage)
let cachedIdentity: { id: string; name: string; role: string } | null = null;

function getCsrfToken(): string {
  if (typeof document === "undefined") return "";
  const match = document.cookie.match(/(?:^|; )csrf_token=([^;]*)/);
  return match ? decodeURIComponent(match[1]) : "";
}

export const authProvider: AuthProvider = {
  login: async ({ phone, otp, rememberMe }) => {
    try {
      const response = await fetch(`${API_URL}/auth/verify-otp`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          phone,
          otp,
          remember_me: rememberMe ?? false,
          client_type: "web",
        }),
      });

      if (!response.ok) {
        const err = await response.json();
        return {
          success: false,
          error: {
            name: err.code || "LoginError",
            message: err.detail || "Authentication failed",
          },
        };
      }

      const data = await response.json();
      cachedIdentity = {
        id: data.user_id,
        name: data.name || "Unknown",
        role: data.role,
      };
      return { success: true, redirectTo: "/" };
    } catch {
      return {
        success: false,
        error: { name: "NetworkError", message: "Could not reach the server" },
      };
    }
  },

  logout: async () => {
    cachedIdentity = null;
    try {
      await fetch(`${API_URL}/auth/logout`, {
        method: "POST",
        credentials: "include",
        headers: { "X-CSRF-Token": getCsrfToken() },
      });
    } catch {
      // Best-effort — cookies will expire anyway
    }
    return { success: true, redirectTo: "/login" };
  },

  check: async () => {
    try {
      const response = await fetch(`${API_URL}/auth/me`, {
        credentials: "include",
      });
      if (response.ok) {
        const data = await response.json();
        cachedIdentity = { id: data.user_id, name: data.name, role: data.role };
        return { authenticated: true };
      }
    } catch {
      // Network error — treat as unauthenticated
    }
    cachedIdentity = null;
    return { authenticated: false, redirectTo: "/login" };
  },

  getIdentity: async () => {
    if (cachedIdentity) {
      return {
        id: cachedIdentity.id,
        name: cachedIdentity.name,
      };
    }

    try {
      const response = await fetch(`${API_URL}/auth/me`, {
        credentials: "include",
      });
      if (response.ok) {
        const data = await response.json();
        cachedIdentity = { id: data.user_id, name: data.name, role: data.role };
        return { id: data.user_id, name: data.name };
      }
    } catch {
      // Swallow — return null below
    }
    return null;
  },

  onError: async (error) => {
    if (error?.statusCode === 401) {
      cachedIdentity = null;
      return { logout: true };
    }
    return { error };
  },
};

export { getCsrfToken };
```

**Step 2: Commit**

```bash
git add packages/admin/src/providers/auth-provider.ts
git commit -m "feat(admin): rewrite auth provider for httpOnly cookie auth"
```

---

## Task 11: Update Admin Data Provider (Cookies + CSRF)

**Files:**
- Modify: `packages/admin/src/providers/data-provider.ts`

**Step 1: Update data provider to use cookies and CSRF header**

Replace `packages/admin/src/providers/data-provider.ts` entirely:

```typescript
import type { DataProvider } from "@refinedev/core";
import { getCsrfToken } from "@/providers/auth-provider";

const API_URL = process.env.NEXT_PUBLIC_API_URL;
if (!API_URL) {
  throw new Error("NEXT_PUBLIC_API_URL environment variable is required");
}

const MUTATING_METHODS = new Set(["POST", "PUT", "DELETE", "PATCH"]);

async function fetchWithAuth(url: string, options: RequestInit = {}) {
  const method = (options.method || "GET").toUpperCase();
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...(MUTATING_METHODS.has(method) ? { "X-CSRF-Token": getCsrfToken() } : {}),
    ...(options.headers || {}),
  };
  return fetch(url, { ...options, headers, credentials: "include" });
}

export const restDataProvider: DataProvider = {
  getList: async ({ resource, pagination, filters, sorters, meta }) => {
    const params = new URLSearchParams();

    if (pagination?.current && pagination?.pageSize) {
      params.set("offset", String((pagination.current - 1) * pagination.pageSize));
      params.set("limit", String(pagination.pageSize));
    }

    if (meta?.params) {
      for (const [k, v] of Object.entries(meta.params)) {
        if (v !== undefined && v !== null) params.set(k, String(v));
      }
    }

    const qs = params.toString();
    const url = `${API_URL}/${resource}${qs ? `?${qs}` : ""}`;
    const res = await fetchWithAuth(url);

    if (!res.ok) {
      throw new Error(`API error ${res.status}: ${await res.text()}`);
    }

    const body = await res.json();

    if (Array.isArray(body)) {
      return { data: body, total: body.length };
    }

    if (body.data && Array.isArray(body.data)) {
      return { data: body.data, total: body.total ?? body.data.length };
    }

    const arrayKey = Object.keys(body).find((k) => Array.isArray(body[k]));
    if (arrayKey) {
      return { data: body[arrayKey], total: body.total ?? body[arrayKey].length };
    }

    return { data: [body], total: 1 };
  },

  getOne: async ({ resource, id }) => {
    const res = await fetchWithAuth(`${API_URL}/${resource}/${id}`);
    if (!res.ok) throw new Error(`API error ${res.status}`);
    return { data: await res.json() };
  },

  create: async ({ resource, variables }) => {
    const res = await fetchWithAuth(`${API_URL}/${resource}`, {
      method: "POST",
      body: JSON.stringify(variables),
    });
    if (!res.ok) throw new Error(`API error ${res.status}`);
    return { data: await res.json() };
  },

  update: async ({ resource, id, variables }) => {
    const res = await fetchWithAuth(`${API_URL}/${resource}/${id}`, {
      method: "PATCH",
      body: JSON.stringify(variables),
    });
    if (!res.ok) throw new Error(`API error ${res.status}`);
    return { data: await res.json() };
  },

  deleteOne: async ({ resource, id }) => {
    const res = await fetchWithAuth(`${API_URL}/${resource}/${id}`, {
      method: "DELETE",
    });
    if (!res.ok) throw new Error(`API error ${res.status}`);
    return { data: { id } as any };
  },

  getApiUrl: () => API_URL!,
};
```

**Step 2: Commit**

```bash
git add packages/admin/src/providers/data-provider.ts
git commit -m "feat(admin): update data provider with cookie auth and CSRF headers"
```

---

## Task 12: Update Mobile Login Screen

**Files:**
- Modify: `packages/mobile/app/(auth)/login.tsx`

**Step 1: Remove mocks and add proper error handling**

Key changes to `packages/mobile/app/(auth)/login.tsx`:

1. **Remove** the entire `__DEV__` block (lines 41-46)
2. **Replace** with real API call for both dev and prod
3. **Add** error message state and display
4. **Add** resend OTP with cooldown
5. **Send** `client_type: "mobile"` in verify request

The `handleSendOtp` function should call the API:

```typescript
const handleSendOtp = async () => {
  if (!validatePhone(phone)) return;
  setLoading(true);
  setError('');
  try {
    const response = await fetch(`${API_URL}/auth/request-otp`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone: `+91${phone}` }),
    });
    if (!response.ok) {
      const err = await response.json();
      setError(err.detail || 'Failed to send OTP');
      return;
    }
    setOtpSent(true);
    setResendCooldown(60);
  } catch {
    setError('Network error. Check your connection.');
  } finally {
    setLoading(false);
  }
};
```

The `handleVerifyOtp` function should always call the API (no `__DEV__` branch):

```typescript
const handleVerifyOtp = async () => {
  setLoading(true);
  setError('');
  try {
    const response = await fetch(`${API_URL}/auth/verify-otp`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        phone: `+91${phone}`,
        otp: otp.join(''),
        client_type: 'mobile',
      }),
    });
    if (!response.ok) {
      const err = await response.json();
      setError(err.detail || 'Verification failed');
      if (err.code === 'OTP_MAX_ATTEMPTS' || err.code === 'OTP_EXPIRED') {
        setOtpSent(false);
        setOtp(['', '', '', '', '', '']);
      }
      return;
    }
    const data = await response.json();
    await SecureStore.setItemAsync('auth_token', data.access_token);
    router.replace('/(tabs)');
  } catch {
    setError('Network error. Check your connection.');
  } finally {
    setLoading(false);
  }
};
```

Add state and UI for `error` and `resendCooldown`:
- `const [error, setError] = useState('');`
- `const [resendCooldown, setResendCooldown] = useState(0);`
- Display error in a `<HelperText type="error">` or `<Snackbar>`
- Show resend link with cooldown timer

Also add `const API_URL = process.env.EXPO_PUBLIC_API_URL;` at the top (remove the import from ApiClient for this page — use fetch directly since the login flow is pre-auth).

**Step 2: Commit**

```bash
git add packages/mobile/app/(auth)/login.tsx
git commit -m "feat(mobile): remove mock auth, use real OTP flow with error handling"
```

---

## Task 13: Update Mobile API Client and Layout

**Files:**
- Modify: `packages/mobile/src/config/api.ts`
- Modify: `packages/mobile/app/_layout.tsx`
- Modify: `packages/mobile/src/services/voice.ts`

**Step 1: Remove localhost fallback from API client**

In `packages/mobile/src/config/api.ts`, line 3, change:

```typescript
// FROM:
const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000/v1';

// TO:
const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL;
if (!API_BASE_URL) {
  throw new Error('EXPO_PUBLIC_API_URL environment variable is required');
}
```

**Step 2: Update root layout to validate token on startup**

In `packages/mobile/app/_layout.tsx`, update the auth check effect (lines 72-81) to validate the token against the API:

```typescript
useEffect(() => {
  (async () => {
    try {
      const token = await SecureStore.getItemAsync('auth_token');
      if (!token) {
        setAuthState('unauthenticated');
        return;
      }
      // Validate token is still valid
      const API_URL = process.env.EXPO_PUBLIC_API_URL;
      const res = await fetch(`${API_URL}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        setAuthState('authenticated');
      } else {
        await SecureStore.deleteItemAsync('auth_token');
        setAuthState('unauthenticated');
      }
    } catch {
      setAuthState('unauthenticated');
    }
  })();
}, []);
```

**Step 3: Remove __DEV__ mock from voice service**

In `packages/mobile/src/services/voice.ts`, remove lines 21-28 (`USE_MOCK`, `DEV_PLACEHOLDER`) and the `if (USE_MOCK)` guard at line 38-40. The function should always attempt the real API call. If the voice endpoint isn't available, it will throw — which callers should handle.

Remove:
```typescript
const USE_MOCK = __DEV__;
const DEV_PLACEHOLDER: VoiceResult = { ... };
```

Remove the early return:
```typescript
if (USE_MOCK) {
  return DEV_PLACEHOLDER;
}
```

Also change line 19:
```typescript
// FROM:
const API_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000/v1';
// TO:
const API_URL = process.env.EXPO_PUBLIC_API_URL;
```

**Step 4: Commit**

```bash
git add packages/mobile/src/config/api.ts packages/mobile/app/_layout.tsx packages/mobile/src/services/voice.ts
git commit -m "feat(mobile): remove all mocks and localhost fallbacks"
```

---

## Task 14: Update .env.example and .gitignore

**Files:**
- Modify: `packages/api/.env.example`
- Verify: `.gitignore` excludes `.env`

**Step 1: Update .env.example**

Replace `packages/api/.env.example`:

```env
# Database
DATABASE_URL=postgresql+asyncpg://pashu:YOUR_PASSWORD@localhost:5432/pashuraksha

# Authentication
JWT_SECRET=GENERATE_WITH_openssl_rand_-hex_32
JWT_EXPIRE_MINUTES=480

# Environment: development | production
ENVIRONMENT=development

# CORS (comma-separated origins)
CORS_ORIGINS=http://localhost:3000,http://localhost:8081,http://localhost:19006

# Sarvam AI (required in production)
SARVAM_API_KEY=

# Rate limiting
RATE_LIMIT_PER_MINUTE=10
```

**Step 2: Verify .gitignore**

Check that `.env` (not `.env.example`) is in `.gitignore`. If not, add it.

**Step 3: Commit**

```bash
git add packages/api/.env.example .gitignore
git commit -m "chore: update .env.example with all required vars, verify .gitignore"
```

---

## Task 15: Integration Smoke Test

**Files:** None (manual verification)

**Step 1: Start the stack**

```bash
cd pashu-erp && docker compose up -d db && cd packages/api && uvicorn app.main:app --reload
```

**Step 2: Test OTP request**

```bash
curl -s -X POST http://localhost:8000/v1/auth/request-otp \
  -H 'Content-Type: application/json' \
  -d '{"phone": "+919900000001"}' | python3 -m json.tool
```

Expected: `{"message": "OTP sent successfully"}` and OTP logged in API console.

**Step 3: Test OTP verify (web — cookies)**

```bash
curl -s -X POST http://localhost:8000/v1/auth/verify-otp \
  -H 'Content-Type: application/json' \
  -d '{"phone": "+919900000001", "otp": "THE_OTP_FROM_CONSOLE", "client_type": "web"}' \
  -c cookies.txt -v 2>&1 | grep -E 'Set-Cookie|user_id|role'
```

Expected: Two `Set-Cookie` headers (token + csrf_token) and JSON body with user_id/role.

**Step 4: Test /me with cookie**

```bash
curl -s http://localhost:8000/v1/auth/me -b cookies.txt | python3 -m json.tool
```

Expected: `{"user_id": "...", "role": "admin", "name": "..."}`.

**Step 5: Test OTP verify (mobile — Bearer token)**

```bash
# Request new OTP first
curl -s -X POST http://localhost:8000/v1/auth/request-otp \
  -H 'Content-Type: application/json' \
  -d '{"phone": "+919900000002"}'

# Verify with client_type=mobile
curl -s -X POST http://localhost:8000/v1/auth/verify-otp \
  -H 'Content-Type: application/json' \
  -d '{"phone": "+919900000002", "otp": "THE_OTP", "client_type": "mobile"}' | python3 -m json.tool
```

Expected: JSON body includes `access_token` field.

**Step 6: Test CSRF protection**

```bash
# POST without CSRF token should fail (when using cookies, not Bearer)
curl -s -X POST http://localhost:8000/v1/animals \
  -H 'Content-Type: application/json' \
  -b cookies.txt \
  -d '{}' | python3 -m json.tool
```

Expected: 403 with `CSRF_MISSING` code.

**Step 7: Test admin login page**

```bash
cd packages/admin && npm run dev
```

Open `http://localhost:3000/login` — should see the login form with +91 prefix input.

**Step 8: Commit nothing — this is verification only**

---

## Execution Order Summary

| Task | Component | Description | Dependencies |
|------|-----------|-------------|--------------|
| 1 | API | OTP model + migration | None |
| 2 | API | OTP provider abstraction | None |
| 3 | API | Auth schemas update | None |
| 4 | API | Auth router rewrite | Tasks 1, 2, 3 |
| 5 | API | Auth middleware (cookie support) | None |
| 6 | API | CSRF middleware + main.py | Task 5 |
| 7 | API | Config validation + .env | None |
| 8 | API | Test fixtures update | Task 4 |
| 9 | Admin | Login page | None |
| 10 | Admin | Auth provider rewrite | None |
| 11 | Admin | Data provider (CSRF) | Task 10 |
| 12 | Mobile | Login screen rewrite | None |
| 13 | Mobile | API client + layout + voice | None |
| 14 | All | .env.example + .gitignore | None |
| 15 | All | Integration smoke test | All above |

**Parallelizable groups:**
- Tasks 1, 2, 3, 5, 7 can run in parallel (no dependencies)
- Tasks 9, 10, 12, 13 can run in parallel (frontend changes, no API dependency for code writing)
- Task 4 depends on 1+2+3
- Task 6 depends on 5
- Task 11 depends on 10
- Task 15 depends on all
