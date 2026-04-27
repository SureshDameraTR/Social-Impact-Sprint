# app/routers/admin_refresh.py
from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import require_admin
from app.models.user import User
from app.services.refresh.disease_sync import DiseaseSyncService
from app.services.refresh.lgd_sync import LGDSyncService
from app.services.refresh.market_prices import AgmarknetSyncService
from app.services.refresh.milk_prices import MilkPriceScraper

router = APIRouter(prefix="/v1/admin/refresh", tags=["Admin — Data Refresh"])


def _get_data_gov_client():
    import app.main as main_mod
    client = getattr(main_mod.app.state, "data_gov_client", None)
    if not client:
        raise HTTPException(503, "data.gov.in client not configured — set DATA_GOV_IN_API_KEY")
    return client


@router.post("/locations")
async def refresh_locations(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = LGDSyncService(data_gov_client=_get_data_gov_client())
    states_result = await service.sync_states(db)
    districts_result = await service.sync_districts(db)
    return {"results": [asdict(states_result), asdict(districts_result)]}


@router.post("/market-prices")
async def refresh_market_prices(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = AgmarknetSyncService(data_gov_client=_get_data_gov_client())
    result = await service.sync_prices(db)
    return {"result": asdict(result)}


@router.post("/milk-prices")
async def refresh_milk_prices(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    from app.services.http_client import get_http_client
    http_client = await get_http_client()
    scraper = MilkPriceScraper(http_client=http_client)
    result = await scraper.sync_prices(db)
    return {"result": asdict(result)}


@router.post("/disease-rules")
async def refresh_disease_rules(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = DiseaseSyncService()
    result = await service.seed_from_hardcoded(db)
    return {"result": asdict(result)}


@router.post("/all")
async def refresh_all(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    from app.services.http_client import get_http_client
    results = []

    try:
        lgd = LGDSyncService(data_gov_client=_get_data_gov_client())
        results.append(asdict(await lgd.sync_states(db)))
        results.append(asdict(await lgd.sync_districts(db)))
    except Exception as e:
        results.append({"source": "LGD", "error": str(e)})

    try:
        agm = AgmarknetSyncService(data_gov_client=_get_data_gov_client())
        results.append(asdict(await agm.sync_prices(db)))
    except Exception as e:
        results.append({"source": "Agmarknet", "error": str(e)})

    try:
        http_client = await get_http_client()
        milk = MilkPriceScraper(http_client=http_client)
        results.append(asdict(await milk.sync_prices(db)))
    except Exception as e:
        results.append({"source": "NDDB/KMF", "error": str(e)})

    disease = DiseaseSyncService()
    results.append(asdict(await disease.seed_from_hardcoded(db)))

    return {"results": results}
