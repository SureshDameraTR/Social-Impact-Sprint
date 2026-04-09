"""Karnataka APMC market rates for livestock products.

Reference prices are now maintained in the ``market_rates`` database table
(see ``app.models.reference.MarketRate``). This module provides async helpers
for querying those rates.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reference import MarketRate


async def get_all_market_rates(db: AsyncSession) -> dict[str, dict]:
    """Return all market rates keyed by product name.

    The returned dict mirrors the old ``KARNATAKA_MARKET_RATES`` structure so
    existing consumers can adapt incrementally.
    """
    result = await db.execute(select(MarketRate).order_by(MarketRate.product))
    rows = result.scalars().all()

    rates: dict[str, dict] = {}
    for row in rows:
        rates[row.product] = {
            "unit": row.unit,
            "min": float(row.min_price),
            "max": float(row.max_price),
            "avg": float(row.avg_price),
            "district": row.district,
            "label": row.label,
        }
    return rates
