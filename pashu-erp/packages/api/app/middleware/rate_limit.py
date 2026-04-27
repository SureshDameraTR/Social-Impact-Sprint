"""Global rate limiting via slowapi.

The ``limiter`` instance is created here (not in ``main.py``) so that
routers can import it for per-endpoint overrides without triggering a
circular import.
"""

from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import settings


def get_client_ip(request: Request) -> str:
    """Get client IP, only trusting X-Forwarded-For behind known proxies."""
    # In development/Docker, trust the direct connection
    remote = get_remote_address(request)
    # Only trust X-Forwarded-For if the direct connection is from a known proxy
    # For now, use remote address directly to prevent spoofing
    return remote or "127.0.0.1"


limiter = Limiter(
    key_func=get_client_ip,
    default_limits=[f"{settings.rate_limit_per_minute}/minute"],
    storage_uri="memory://",
)
