"""Shared fixtures for PashuRaksha API unit tests.

Unit tests run against a test client with mocked database dependencies.
No real database or external services required.
"""

# ---------------------------------------------------------------------------
# Environment setup — must happen before importing app modules
# ---------------------------------------------------------------------------
import os
import uuid
from collections.abc import AsyncGenerator
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import jwt
import pytest
from httpx import ASGITransport, AsyncClient

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/test")
os.environ.setdefault(
    "JWT_SECRET",
    "a" * 64,  # 64 hex chars = 256 bits, satisfies validation
)
os.environ.setdefault("ENVIRONMENT", "development")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:3000")


# ---------------------------------------------------------------------------
# Fake user factory
# ---------------------------------------------------------------------------


def _make_user(
    role: str = "farmer",
    user_id: str | None = None,
    name: str = "Test User",
    phone: str = "+919900000099",
    district: str = "Tumkur",
    village_code: str = "629001",
    gender: str = "female",
) -> MagicMock:
    """Create a mock User ORM object with the given role."""
    user = MagicMock()
    user.id = user_id or str(uuid.uuid4())
    user.role = role
    user.name = name
    user.phone = phone
    user.lang_pref = "kn"
    user.location_district = district
    user.location_state = "Karnataka"
    user.village_code = village_code
    user.gender = gender
    user.preferences = {}
    user.aadhaar_hash = None
    user.aadhaar_last4 = None
    user.created_at = datetime.now(timezone.utc)
    user.updated_at = datetime.now(timezone.utc)
    return user


# ---------------------------------------------------------------------------
# Shared user IDs (stable across fixtures)
# ---------------------------------------------------------------------------

FARMER_USER_ID = str(uuid.uuid4())
ADMIN_USER_ID = str(uuid.uuid4())
VET_USER_ID = str(uuid.uuid4())
MILK_CENTER_USER_ID = str(uuid.uuid4())


# ---------------------------------------------------------------------------
# JWT token helpers
# ---------------------------------------------------------------------------

_JWT_SECRET = os.environ["JWT_SECRET"]
_JWT_ALGORITHM = "HS256"


def _make_token(user_id: str) -> str:
    """Create a valid JWT token for the given user ID."""
    payload = {
        "sub": user_id,
        "exp": datetime(2099, 1, 1, tzinfo=timezone.utc).timestamp(),
    }
    return jwt.encode(payload, _JWT_SECRET, algorithm=_JWT_ALGORITHM)


# ---------------------------------------------------------------------------
# User fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def farmer_user() -> MagicMock:
    return _make_user(
        role="farmer",
        user_id=FARMER_USER_ID,
        name="Lakshmi Devi",
        phone="+919900000002",
    )


@pytest.fixture
def admin_user() -> MagicMock:
    return _make_user(
        role="admin",
        user_id=ADMIN_USER_ID,
        name="Admin User",
        phone="+919900000001",
    )


@pytest.fixture
def vet_user() -> MagicMock:
    return _make_user(
        role="vet",
        user_id=VET_USER_ID,
        name="Dr. Ramesh",
        phone="+919900000003",
    )


@pytest.fixture
def milk_center_user() -> MagicMock:
    return _make_user(
        role="milk_center",
        user_id=MILK_CENTER_USER_ID,
        name="Milk Center Staff",
        phone="+919900000004",
    )


# ---------------------------------------------------------------------------
# Auth token fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def farmer_token() -> str:
    return _make_token(FARMER_USER_ID)


@pytest.fixture
def admin_token() -> str:
    return _make_token(ADMIN_USER_ID)


@pytest.fixture
def vet_token() -> str:
    return _make_token(VET_USER_ID)


@pytest.fixture
def milk_center_token() -> str:
    return _make_token(MILK_CENTER_USER_ID)


# ---------------------------------------------------------------------------
# Auth header helpers
# ---------------------------------------------------------------------------


def auth_header(token: str) -> dict[str, str]:
    """Build an Authorization header dict."""
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# Mock DB session fixture
# ---------------------------------------------------------------------------


def _auto_populate_id(obj: object) -> None:
    """Simulate DB auto-populating id and timestamps on refresh.

    Real PostgreSQL sets these via ``server_default`` — mock them here so that
    ``response_model`` validation passes without a real database.
    """
    _now = datetime.now(timezone.utc)

    if not hasattr(obj, "id") or obj.id is None:
        obj.id = str(uuid.uuid4())
    if not hasattr(obj, "created_at") or obj.created_at is None:
        obj.created_at = _now
    if not hasattr(obj, "updated_at") or obj.updated_at is None:
        obj.updated_at = _now

    # Common server-default datetime columns across various models
    for ts_field in ("recorded_at", "filed_at", "event_date", "administered_at"):
        if hasattr(obj, ts_field) and getattr(obj, ts_field) is None:
            setattr(obj, ts_field, _now)

    # Set a default status for Transaction / Claim models
    if hasattr(obj, "amount") and (not hasattr(obj, "status") or obj.status is None):
        obj.status = "completed"
    elif hasattr(obj, "status") and obj.status is None:
        obj.status = "completed"


@pytest.fixture
def mock_db() -> AsyncMock:
    """Create a mock async database session."""
    session = AsyncMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock(side_effect=_auto_populate_id)
    session.add = MagicMock()
    session.delete = AsyncMock()
    session.get = AsyncMock()
    session.rollback = AsyncMock()
    return session


# ---------------------------------------------------------------------------
# App + Client fixture with dependency overrides
# ---------------------------------------------------------------------------


@pytest.fixture
async def client(
    farmer_user: MagicMock,
    mock_db: AsyncMock,
) -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client with farmer auth and mocked DB.

    For admin/vet tests, use client_as_admin or client_as_vet instead.
    """
    # Import app lazily to avoid import-time settings validation issues
    from app.database import get_db
    from app.main import create_app
    from app.middleware.auth import get_current_user

    app = create_app()

    async def _override_db():
        yield mock_db

    async def _override_auth():
        return farmer_user

    app.dependency_overrides[get_db] = _override_db
    app.dependency_overrides[get_current_user] = _override_auth

    # Include a valid JWT in headers so the CSRF middleware passes mutating requests
    _headers = {"Authorization": f"Bearer {_make_token(FARMER_USER_ID)}"}
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", headers=_headers) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def client_as_admin(
    admin_user: MagicMock,
    mock_db: AsyncMock,
) -> AsyncGenerator[AsyncClient, None]:
    """Test client authenticated as admin."""
    from app.database import get_db
    from app.main import create_app
    from app.middleware.auth import get_current_user, require_admin, require_vet_or_admin

    app = create_app()

    async def _override_db():
        yield mock_db

    async def _override_auth():
        return admin_user

    app.dependency_overrides[get_db] = _override_db
    app.dependency_overrides[get_current_user] = _override_auth
    app.dependency_overrides[require_admin] = _override_auth
    app.dependency_overrides[require_vet_or_admin] = _override_auth

    _headers = {"Authorization": f"Bearer {_make_token(ADMIN_USER_ID)}"}
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", headers=_headers) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def client_as_vet(
    vet_user: MagicMock,
    mock_db: AsyncMock,
) -> AsyncGenerator[AsyncClient, None]:
    """Test client authenticated as vet."""
    from app.database import get_db
    from app.main import create_app
    from app.middleware.auth import get_current_user, require_vet_or_admin

    app = create_app()

    async def _override_db():
        yield mock_db

    async def _override_auth():
        return vet_user

    app.dependency_overrides[get_db] = _override_db
    app.dependency_overrides[get_current_user] = _override_auth
    app.dependency_overrides[require_vet_or_admin] = _override_auth

    _headers = {"Authorization": f"Bearer {_make_token(VET_USER_ID)}"}
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", headers=_headers) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def client_as_milk_center(
    milk_center_user: MagicMock,
    mock_db: AsyncMock,
) -> AsyncGenerator[AsyncClient, None]:
    """Test client authenticated as milk center staff."""
    from app.database import get_db
    from app.main import create_app
    from app.middleware.auth import get_current_user

    app = create_app()

    async def _override_db():
        yield mock_db

    async def _override_auth():
        return milk_center_user

    # Also override the milk_center require function
    from app.routers.milk_center import require_milk_center_staff

    app.dependency_overrides[get_db] = _override_db
    app.dependency_overrides[get_current_user] = _override_auth
    app.dependency_overrides[require_milk_center_staff] = _override_auth

    _headers = {"Authorization": f"Bearer {_make_token(MILK_CENTER_USER_ID)}"}
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", headers=_headers) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def client_no_auth(
    mock_db: AsyncMock,
) -> AsyncGenerator[AsyncClient, None]:
    """Test client with NO auth override — triggers 401/403."""
    from app.database import get_db
    from app.main import create_app

    app = create_app()

    async def _override_db():
        yield mock_db

    app.dependency_overrides[get_db] = _override_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
