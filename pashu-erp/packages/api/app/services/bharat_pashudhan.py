"""Client for Bharat Pashudhan (national animal registry) API.

Requires BHARAT_PASHUDHAN_API_URL to be configured in settings.
Raises ServiceNotConfiguredError when the URL is not set.
"""

from datetime import datetime, timezone
from urllib.parse import quote
from uuid import UUID

from app.config import settings
from app.services.circuit_breakers import registry_breaker
from app.services.errors import ServiceNotConfiguredError
from app.services.http_client import get_http_client, retry_on_network


@registry_breaker
@retry_on_network
async def lookup_animal(pashu_aadhaar_id: str) -> dict | None:
    """Look up an animal in the national Bharat Pashudhan registry.

    Returns the animal record dict with added lookup metadata,
    or None if the animal is not found (404).

    Raises:
        ServiceNotConfiguredError: If BHARAT_PASHUDHAN_API_URL is not set.
        httpx.HTTPStatusError: On non-404 HTTP errors.
    """
    if not settings.bharat_pashudhan_api_url:
        raise ServiceNotConfiguredError("BHARAT_PASHUDHAN_API_URL")

    client = await get_http_client()
    safe_id = quote(pashu_aadhaar_id, safe="")
    resp = await client.get(f"{settings.bharat_pashudhan_api_url}/animals/{safe_id}")
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    record = resp.json()
    record["lookup_timestamp"] = datetime.now(timezone.utc).isoformat()
    record["source"] = "Bharat Pashudhan National Database"
    return record


@registry_breaker
@retry_on_network
async def sync_animal(animal_id: UUID) -> dict:
    """Sync a local animal record with the national registry.

    Raises:
        ServiceNotConfiguredError: If BHARAT_PASHUDHAN_API_URL is not set.
        httpx.HTTPStatusError: On HTTP errors.
    """
    if not settings.bharat_pashudhan_api_url:
        raise ServiceNotConfiguredError("BHARAT_PASHUDHAN_API_URL")

    client = await get_http_client()
    resp = await client.post(
        f"{settings.bharat_pashudhan_api_url}/sync",
        json={"animal_id": str(animal_id)},
    )
    resp.raise_for_status()
    return resp.json()
