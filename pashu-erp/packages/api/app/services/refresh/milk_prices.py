# app/services/refresh/milk_prices.py
import logging
import re

from bs4 import BeautifulSoup
from httpx import AsyncClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reference import MarketRate
from app.services.refresh.base import RefreshResult

logger = logging.getLogger(__name__)

NDDB_STATS_URL = "https://www.nddb.coop/information/stats/milkprocprice"


class MilkPriceScraper:
    def __init__(self, http_client: AsyncClient):
        self._client = http_client

    def _parse_price_table(self, html: str) -> list[dict]:
        soup = BeautifulSoup(html, "html.parser")
        prices = []

        table = soup.find("table", class_="views-table")
        if not table:
            return prices

        rows = table.find("tbody")
        if not rows:
            return prices

        for tr in rows.find_all("tr"):
            cells = tr.find_all("td")
            if len(cells) >= 2:
                state = cells[0].get_text(strip=True)
                price_text = cells[1].get_text(strip=True)
                price_clean = re.sub(r"[^\d.]", "", price_text)
                try:
                    price = float(price_clean) if price_clean else None
                except ValueError:
                    price = None

                if state and price:
                    prices.append({"state": state, "price_per_litre": price})

        return prices

    async def sync_prices(self, db: AsyncSession) -> RefreshResult:
        result = RefreshResult(source="NDDB/KMF")

        try:
            resp = await self._client.get(NDDB_STATS_URL, timeout=30.0)
            resp.raise_for_status()
            prices = self._parse_price_table(resp.text)
            result.records_fetched = len(prices)

            await db.execute(
                delete(MarketRate).where(MarketRate.source == "NDDB")
            )

            for p in prices:
                db.add(
                    MarketRate(
                        product="milk",
                        district=p["state"],
                        min_price=p["price_per_litre"],
                        max_price=p["price_per_litre"],
                        avg_price=p["price_per_litre"],
                        unit="litre",
                        source="NDDB",
                        label=f"NDDB - {p['state']}",
                    )
                )
                result.records_inserted += 1

            await db.commit()
        except Exception as e:
            result.errors.append(str(e))
            logger.error("NDDB scrape failed: %s", e)

        return result.complete()
