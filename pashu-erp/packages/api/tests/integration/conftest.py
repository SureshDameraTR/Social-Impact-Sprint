"""Integration test fixtures — real PostgreSQL, no mocks.

Requires a running PostgreSQL instance at localhost:5433.
Start it with: docker compose -f docker-compose.test.yml up -d
"""

import os
import socket
from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient


def _pg_reachable(host: str = "localhost", port: int = 5433) -> bool:
    """Check if PostgreSQL is reachable on the expected port."""
    try:
        with socket.create_connection((host, port), timeout=1):
            return True
    except (OSError, ConnectionRefusedError):
        return False


_PG_AVAILABLE = _pg_reachable()


def pytest_collection_modifyitems(config, items):  # noqa: ANN001
    """Skip all integration tests when PostgreSQL is not reachable."""
    if _PG_AVAILABLE:
        return
    skip_marker = pytest.mark.skip(
        reason="PostgreSQL not available at localhost:5433 (start with docker compose)"
    )
    for item in items:
        if "integration" in str(item.fspath):
            item.add_marker(skip_marker)


# Override environment BEFORE importing any app modules so that Settings
# picks up the test database URL and a valid JWT secret.
os.environ["DATABASE_URL"] = (
    "postgresql+asyncpg://pashu_test:test_password@localhost:5433/pashuraksha_test"
)
os.environ["JWT_SECRET"] = "a" * 64
os.environ["ENVIRONMENT"] = "development"
os.environ["CORS_ORIGINS"] = "http://localhost:3000"

from sqlalchemy import text  # noqa: E402
from sqlalchemy.ext.asyncio import (  # noqa: E402
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.database import get_db  # noqa: E402
from app.main import create_app  # noqa: E402
from app.middleware.auth import _user_cache  # noqa: E402
from app.middleware.rate_limit import limiter  # noqa: E402
from app.models.base import Base  # noqa: E402

TEST_DATABASE_URL = os.environ["DATABASE_URL"]


@pytest.fixture(autouse=True)
def _skip_without_pg():
    """Skip integration tests when PostgreSQL is not available."""
    if not _PG_AVAILABLE:
        pytest.skip("PostgreSQL not available at localhost:5433")


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    """Clear the in-memory rate limiter and auth cache before each test."""
    limiter.reset()
    _user_cache.clear()
    yield
    limiter.reset()
    _user_cache.clear()


@pytest.fixture
async def _test_engine():
    """Create a fresh engine per test to avoid cross-loop issues with pytest-asyncio."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False, pool_size=5)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    # Truncate all tables for isolation, then dispose.
    async with engine.begin() as conn:
        result = await conn.execute(
            text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
        )
        tables = [row[0] for row in result]
        if tables:
            await conn.execute(text(f"TRUNCATE {', '.join(tables)} CASCADE"))
    await engine.dispose()


@pytest.fixture
def _test_sessionmaker(_test_engine):
    return async_sessionmaker(_test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture
async def db_session(_test_sessionmaker) -> AsyncGenerator[AsyncSession, None]:
    """Provide a real async database session for direct DB queries in tests."""
    async with _test_sessionmaker() as session:
        yield session


@pytest.fixture
async def integration_client(_test_sessionmaker) -> AsyncGenerator[AsyncClient, None]:
    """ASGI test client wired to the real PostgreSQL database.

    Each HTTP request gets its own session from the sessionmaker — no shared
    session, which avoids asyncpg 'another operation in progress' errors.
    """
    app = create_app()

    async def _override_db() -> AsyncGenerator[AsyncSession, None]:
        async with _test_sessionmaker() as session:
            yield session

    app.dependency_overrides[get_db] = _override_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
