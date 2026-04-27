"""Tests for storage service client (app.services.storage_service)."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.services.errors import ServiceNotConfiguredError
from app.services.storage_service import get_file, list_files, upload_file


def _patch_client(mc):
    """Patch get_http_client to return the mock client."""
    return patch(
        "app.services.storage_service.get_http_client",
        new_callable=AsyncMock,
        return_value=mc,
    )


# ---------------------------------------------------------------------------
# upload_file
# ---------------------------------------------------------------------------


class TestUploadFile:
    async def test_upload_success(self):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"file_id": "f1", "url": "/files/f1"}
        mock_resp.raise_for_status = MagicMock()

        mc = AsyncMock()
        mc.post.return_value = mock_resp

        with (
            patch("app.services.storage_service.settings") as s,
            _patch_client(mc),
        ):
            s.storage_api_url = "http://mock:8001/storage"
            result = await upload_file(
                file_bytes=b"image-data",
                filename="photo.jpg",
                content_type="image/jpeg",
                category="animal_photo",
                entity_type="animal",
                entity_id="a1",
            )

        assert result["file_id"] == "f1"
        call_kwargs = mc.post.call_args
        assert "files" in call_kwargs.kwargs
        assert "data" in call_kwargs.kwargs

    async def test_upload_not_configured_raises(self):
        with patch("app.services.storage_service.settings") as s:
            s.storage_api_url = ""
            with pytest.raises(ServiceNotConfiguredError):
                await upload_file(
                    b"data", "f.txt", "text/plain", "doc", "animal", "a1"
                )

    async def test_upload_http_error(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_resp.raise_for_status.side_effect = httpx.HTTPStatusError(
            "server error", request=MagicMock(), response=mock_resp
        )

        mc = AsyncMock()
        mc.post.return_value = mock_resp

        with (
            patch("app.services.storage_service.settings") as s,
            _patch_client(mc),
        ):
            s.storage_api_url = "http://mock:8001/storage"
            with pytest.raises(httpx.HTTPStatusError):
                await upload_file(
                    b"data", "f.txt", "text/plain", "doc", "animal", "a1"
                )


# ---------------------------------------------------------------------------
# get_file
# ---------------------------------------------------------------------------


class TestGetFile:
    async def test_download_returns_bytes_and_content_type(self):
        mock_resp = MagicMock()
        mock_resp.content = b"file-bytes"
        mock_resp.headers = {"content-type": "image/jpeg"}
        mock_resp.raise_for_status = MagicMock()

        mc = AsyncMock()
        mc.get.return_value = mock_resp

        with (
            patch("app.services.storage_service.settings") as s,
            _patch_client(mc),
        ):
            s.storage_api_url = "http://mock:8001/storage"
            content, ct = await get_file("f1")

        assert content == b"file-bytes"
        assert ct == "image/jpeg"

    async def test_download_missing_content_type_defaults(self):
        """Missing content-type header defaults to application/octet-stream."""
        mock_resp = MagicMock()
        mock_resp.content = b"data"
        mock_resp.headers = {}
        mock_resp.raise_for_status = MagicMock()

        mc = AsyncMock()
        mc.get.return_value = mock_resp

        with (
            patch("app.services.storage_service.settings") as s,
            _patch_client(mc),
        ):
            s.storage_api_url = "http://mock:8001/storage"
            _, ct = await get_file("f1")

        assert ct == "application/octet-stream"


# ---------------------------------------------------------------------------
# list_files
# ---------------------------------------------------------------------------


class TestListFiles:
    async def test_list_with_filters(self):
        payload = {"data": [{"file_id": "f1"}], "total": 1}

        mock_resp = MagicMock()
        mock_resp.json.return_value = payload
        mock_resp.raise_for_status = MagicMock()

        mc = AsyncMock()
        mc.get.return_value = mock_resp

        with (
            patch("app.services.storage_service.settings") as s,
            _patch_client(mc),
        ):
            s.storage_api_url = "http://mock:8001/storage"
            result = await list_files(entity_type="animal", entity_id="a1")

        assert result["total"] == 1
        call_kwargs = mc.get.call_args
        assert call_kwargs.kwargs["params"]["entity_type"] == "animal"
