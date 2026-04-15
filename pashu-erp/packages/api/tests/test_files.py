"""Unit tests for File upload/download endpoints — /v1/files."""

import io
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from httpx import AsyncClient


# ---------------------------------------------------------------------------
# POST /v1/files — Upload
# ---------------------------------------------------------------------------


class TestUploadFile:
    async def test_upload_success(self, client: AsyncClient) -> None:
        """POST with valid file returns 200."""
        with patch(
            "app.routers.files.storage_service.upload_file",
            new_callable=AsyncMock,
            return_value={
                "file_id": "abc-123",
                "url": "http://storage/files/abc-123",
            },
        ):
            resp = await client.post(
                "/v1/files",
                files={"file": ("test.jpg", b"fake image data", "image/jpeg")},
                data={
                    "category": "photo",
                    "entity_type": "animal",
                    "entity_id": "animal-uuid-here",
                },
            )
            assert resp.status_code == 200

    async def test_upload_storage_error(self, client: AsyncClient) -> None:
        """POST when storage is down returns 502."""
        with patch(
            "app.routers.files.storage_service.upload_file",
            new_callable=AsyncMock,
            side_effect=httpx.RequestError("timeout"),
        ):
            resp = await client.post(
                "/v1/files",
                files={"file": ("test.jpg", b"data", "image/jpeg")},
                data={
                    "category": "photo",
                    "entity_type": "animal",
                    "entity_id": "id",
                },
            )
            assert resp.status_code == 502

    async def test_upload_no_auth(self, client_no_auth: AsyncClient) -> None:
        """POST without auth returns 401/403."""
        resp = await client_no_auth.post(
            "/v1/files",
            files={"file": ("test.jpg", b"data", "image/jpeg")},
            data={
                "category": "photo",
                "entity_type": "animal",
                "entity_id": "id",
            },
        )
        assert resp.status_code in (401, 403)


# ---------------------------------------------------------------------------
# GET /v1/files/{file_id} — Download
# ---------------------------------------------------------------------------


class TestGetFile:
    async def test_download_success(self, client: AsyncClient) -> None:
        """GET returns 200 with file content."""
        with patch(
            "app.routers.files.storage_service.get_file",
            new_callable=AsyncMock,
            return_value=(b"image-bytes", "image/jpeg"),
        ):
            resp = await client.get("/v1/files/abc-123")
            assert resp.status_code == 200
            assert resp.headers["content-type"] == "image/jpeg"

    async def test_download_storage_error(self, client: AsyncClient) -> None:
        """GET when storage is down returns 502."""
        with patch(
            "app.routers.files.storage_service.get_file",
            new_callable=AsyncMock,
            side_effect=httpx.RequestError("timeout"),
        ):
            resp = await client.get("/v1/files/abc-123")
            assert resp.status_code == 502


# ---------------------------------------------------------------------------
# GET /v1/files — List
# ---------------------------------------------------------------------------


class TestListFiles:
    async def test_list_success(self, client: AsyncClient) -> None:
        """GET returns 200."""
        with patch(
            "app.routers.files.storage_service.list_files",
            new_callable=AsyncMock,
            return_value={"data": [], "total": 0},
        ):
            resp = await client.get("/v1/files")
            assert resp.status_code == 200

    async def test_list_with_filters(self, client: AsyncClient) -> None:
        """GET with entity filters returns 200."""
        with patch(
            "app.routers.files.storage_service.list_files",
            new_callable=AsyncMock,
            return_value={"data": [], "total": 0},
        ):
            resp = await client.get(
                "/v1/files?entity_type=animal&entity_id=uuid-here"
            )
            assert resp.status_code == 200
