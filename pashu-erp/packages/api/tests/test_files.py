"""Unit tests for File upload/download endpoints — /v1/files."""

from unittest.mock import AsyncMock, patch

import httpx
from httpx import AsyncClient

# ---------------------------------------------------------------------------
# POST /v1/files — Upload
# ---------------------------------------------------------------------------


# Valid JPEG file content (starts with JPEG magic bytes FF D8 FF)
_JPEG_HEADER = b"\xff\xd8\xff\xe0" + b"\x00" * 100

# Valid PNG file content (starts with PNG magic bytes)
_PNG_HEADER = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100


class TestUploadFile:
    async def test_upload_success(self, client: AsyncClient) -> None:
        """POST with valid file returns 200."""
        with patch(
            "app.routers.files.storage_service.upload_file",
            new_callable=AsyncMock,
            return_value={
                "file_id": "abc-123",
                "url": "http://storage/files/abc-123",
                "filename": "test.jpg",
                "content_type": "image/jpeg",
                "size_bytes": 104,
                "category": "photo",
                "entity_type": "animal",
                "entity_id": "animal-uuid-here",
                "created_at": "2026-04-16T00:00:00Z",
            },
        ):
            resp = await client.post(
                "/v1/files",
                files={"file": ("test.jpg", _JPEG_HEADER, "image/jpeg")},
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
                files={"file": ("test.jpg", _JPEG_HEADER, "image/jpeg")},
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
            resp = await client.get("/v1/files?entity_type=animal&entity_id=uuid-here")
            assert resp.status_code == 200
