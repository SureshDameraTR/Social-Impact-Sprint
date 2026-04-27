# app/services/refresh/market_prices.py
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reference import MarketRate
from app.services.data_gov_client import DataGovClient
from app.services.refresh.base import RefreshResult

logger = logging.getLogger(__name__)

AGMARKNET_RESOURCE = "9ef84268-d588-465a-a308-a864a43d0070"


class AgmarknetSyncService:
    def __init__(self, data_gov_client: DataGovClient):
        self._client = data_gov_client

    async def sync_prices(
        self,
        db: AsyncSession,
        state: str = "Karnataka",
    ) -> RefreshResult:
        result = RefreshResult(source="data.gov.in/Agmarknet")

        records = await self._client.fetch_all_records(
            AGMARKNET_RESOURCE,
            filters={"State.keyword": state},
            page_size=500,
            max_records=5000,
        )
        result.records_fetched = len(records)

        for rec in records:
            try:
                district = rec.get("district", "").strip()
                product = rec.get("commodity", "").strip()
                modal = float(rec.get("modal_price", 0))
                if not district or not product or not modal:
                    continue

                db.add(MarketRate(
                    product=product,
                    district=district,
                    min_price=float(rec.get("min_price", 0)),
                    max_price=float(rec.get("max_price", 0)),
                    avg_price=modal,
                    unit="quintal",
                    source="Agmarknet",
                    label=rec.get("market", ""),
                ))
                result.records_inserted += 1
            except (ValueError, TypeError) as e:
                result.errors.append(f"Parse error for {rec}: {e}")

        await db.commit()
        return result.complete()
