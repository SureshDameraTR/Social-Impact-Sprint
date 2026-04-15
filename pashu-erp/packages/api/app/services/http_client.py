"""Shared HTTP client with connection pooling and retry logic."""

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

_client: httpx.AsyncClient | None = None


async def get_http_client() -> httpx.AsyncClient:
    """Return the shared pooled HTTP client, creating it if needed."""
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(
            timeout=10.0,
            limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
        )
    return _client


async def close_http_client() -> None:
    """Gracefully close the shared HTTP client."""
    global _client
    if _client and not _client.is_closed:
        await _client.aclose()
        _client = None


# Re-export retry helpers so service modules can import from one place.
retry_on_network = retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=0.5, max=5),
    retry=retry_if_exception_type((httpx.ConnectError, httpx.TimeoutException)),
    reraise=True,
)
