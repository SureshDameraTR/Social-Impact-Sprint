# app/services/data_gov_client.py
import logging

from httpx import AsyncClient
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class DataGovClient:
    """Reusable async client for data.gov.in open data API."""

    def __init__(
        self,
        http_client: AsyncClient,
        api_key: str,
        base_url: str = "https://api.data.gov.in",
    ):
        self._client = http_client
        self._api_key = api_key
        self._base_url = base_url

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10), reraise=True)
    async def fetch_resource(
        self,
        resource_id: str,
        limit: int = 100,
        offset: int = 0,
        filters: dict[str, str] | None = None,
    ) -> dict:
        """Fetch a single page of records from a data.gov.in resource."""
        url = f"{self._base_url}/resource/{resource_id}"
        params: dict[str, str | int] = {
            "api-key": self._api_key,
            "format": "json",
            "limit": limit,
            "offset": offset,
        }
        if filters:
            for k, v in filters.items():
                params[f"filters[{k}]"] = v

        logger.info(
            "Fetching data.gov.in resource",
            extra={"resource_id": resource_id, "limit": limit, "offset": offset},
        )
        resp = await self._client.get(url, params=params, timeout=30.0)
        resp.raise_for_status()
        return resp.json()

    async def fetch_all_records(
        self,
        resource_id: str,
        page_size: int = 500,
        filters: dict[str, str] | None = None,
        max_records: int = 50000,
    ) -> list[dict]:
        """Auto-paginate through all records for a resource."""
        all_records: list[dict] = []
        offset = 0

        while offset < max_records:
            result = await self.fetch_resource(
                resource_id, limit=page_size, offset=offset, filters=filters
            )
            records = result.get("records", [])
            all_records.extend(records)

            if len(records) < page_size:
                break
            offset += page_size

        return all_records
