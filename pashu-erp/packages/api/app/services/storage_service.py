"""Storage service client.

Proxies file upload/download requests to the configured storage backend.
"""

from app.config import settings
from app.services.circuit_breakers import storage_breaker
from app.services.errors import ServiceNotConfiguredError
from app.services.http_client import get_http_client, retry_on_network


def _base_url() -> str:
    url = settings.storage_api_url
    if not url:
        raise ServiceNotConfiguredError("STORAGE_API_URL")
    return url.rstrip("/")


@storage_breaker
@retry_on_network
async def upload_file(
    file_bytes: bytes,
    filename: str,
    content_type: str,
    category: str,
    entity_type: str,
    entity_id: str,
) -> dict:
    """Upload a file to the storage backend."""
    base = _base_url()

    files = {"file": (filename, file_bytes, content_type)}
    data = {
        "category": category,
        "entity_type": entity_type,
        "entity_id": entity_id,
    }

    client = await get_http_client()
    resp = await client.post(f"{base}/files", files=files, data=data)
    resp.raise_for_status()
    return resp.json()


@storage_breaker
@retry_on_network
async def get_file(file_id: str) -> tuple[bytes, str]:
    """Download a file from the storage backend.

    Returns a tuple of (file_bytes, content_type).
    """
    base = _base_url()

    client = await get_http_client()
    resp = await client.get(f"{base}/files/{file_id}")
    resp.raise_for_status()
    ct = resp.headers.get("content-type", "application/octet-stream")
    return resp.content, ct


@storage_breaker
@retry_on_network
async def list_files(
    entity_type: str | None = None,
    entity_id: str | None = None,
) -> dict:
    """List files with optional entity filters."""
    base = _base_url()
    params: dict = {}
    if entity_type is not None:
        params["entity_type"] = entity_type
    if entity_id is not None:
        params["entity_id"] = entity_id

    client = await get_http_client()
    resp = await client.get(f"{base}/files", params=params)
    resp.raise_for_status()
    return resp.json()
