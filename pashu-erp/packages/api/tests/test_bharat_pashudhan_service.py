"""Tests for Bharat Pashudhan service client (app.services.bharat_pashudhan)."""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import httpx
import pytest

from app.services.bharat_pashudhan import lookup_animal, sync_animal
from app.services.errors import ServiceNotConfiguredError


def _patch_client(mc):
    """Patch get_http_client to return the mock client."""
    return patch(
        "app.services.bharat_pashudhan.get_http_client",
        new_callable=AsyncMock,
        return_value=mc,
    )


# ---------------------------------------------------------------------------
# lookup_animal
# ---------------------------------------------------------------------------


class TestLookupAnimal:
    async def test_found_returns_record_with_metadata(self):
        """Successful lookup returns dict with lookup_timestamp and source."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "pashu_aadhaar_id": "123456789012",
            "species": "cattle",
            "breed": "Gir",
        }
        mock_resp.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_resp

        with (
            patch("app.services.bharat_pashudhan.settings") as mock_settings,
            _patch_client(mock_client),
        ):
            mock_settings.bharat_pashudhan_api_url = (
                "http://mock:8001/registry"
            )
            result = await lookup_animal("123456789012")

        assert result is not None
        assert result["species"] == "cattle"
        assert "lookup_timestamp" in result
        assert result["source"] == "Bharat Pashudhan National Database"

    async def test_not_found_returns_none(self):
        """404 response returns None."""
        mock_resp = MagicMock()
        mock_resp.status_code = 404

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_resp

        with (
            patch("app.services.bharat_pashudhan.settings") as mock_settings,
            _patch_client(mock_client),
        ):
            mock_settings.bharat_pashudhan_api_url = (
                "http://mock:8001/registry"
            )
            result = await lookup_animal("000000000000")

        assert result is None

    async def test_not_configured_raises(self):
        """Raises ServiceNotConfiguredError when URL is empty."""
        with patch("app.services.bharat_pashudhan.settings") as mock_settings:
            mock_settings.bharat_pashudhan_api_url = ""
            with pytest.raises(ServiceNotConfiguredError):
                await lookup_animal("123456789012")

    async def test_server_error_propagates(self):
        """Non-404 HTTP errors propagate as HTTPStatusError."""
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_resp.raise_for_status.side_effect = httpx.HTTPStatusError(
            "server error", request=MagicMock(), response=mock_resp
        )

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_resp

        with (
            patch("app.services.bharat_pashudhan.settings") as mock_settings,
            _patch_client(mock_client),
        ):
            mock_settings.bharat_pashudhan_api_url = (
                "http://mock:8001/registry"
            )
            with pytest.raises(httpx.HTTPStatusError):
                await lookup_animal("123456789012")


# ---------------------------------------------------------------------------
# sync_animal
# ---------------------------------------------------------------------------


class TestSyncAnimal:
    async def test_sync_success(self):
        animal_id = uuid4()
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "synced": True,
            "animal_id": str(animal_id),
        }
        mock_resp.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_resp

        with (
            patch("app.services.bharat_pashudhan.settings") as mock_settings,
            _patch_client(mock_client),
        ):
            mock_settings.bharat_pashudhan_api_url = (
                "http://mock:8001/registry"
            )
            result = await sync_animal(animal_id)

        assert result["synced"] is True

    async def test_sync_not_configured_raises(self):
        with patch("app.services.bharat_pashudhan.settings") as mock_settings:
            mock_settings.bharat_pashudhan_api_url = ""
            with pytest.raises(ServiceNotConfiguredError):
                await sync_animal(uuid4())
