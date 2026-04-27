# app/services/refresh/lgd_sync.py
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.location import District, State
from app.services.data_gov_client import DataGovClient
from app.services.refresh.base import RefreshResult

logger = logging.getLogger(__name__)

LGD_STATES_RESOURCE = "0f209e73-53e8-4e3c-a56f-3ec5c4fd3278"
LGD_DISTRICTS_RESOURCE = "cfee38c5-6f3e-4bfb-b02f-e172c5e3567f"


class LGDSyncService:
    def __init__(self, data_gov_client: DataGovClient):
        self._client = data_gov_client

    async def sync_states(self, db: AsyncSession) -> RefreshResult:
        result = RefreshResult(source="data.gov.in/LGD")
        records = await self._client.fetch_all_records(LGD_STATES_RESOURCE)
        result.records_fetched = len(records)

        existing = (await db.execute(select(State))).scalars().all()
        existing_by_code = {s.lgd_code: s for s in existing}

        for rec in records:
            code = int(rec.get("state_code", 0))
            name = rec.get("state_name_english_", "").strip()
            if not code or not name:
                continue

            if code in existing_by_code:
                state = existing_by_code[code]
                if state.name != name:
                    state.name = name
                    result.records_updated += 1
                else:
                    result.records_unchanged += 1
            else:
                db.add(State(lgd_code=code, name=name))
                result.records_inserted += 1

        await db.commit()
        return result.complete()

    async def sync_districts(
        self, db: AsyncSession, state_lgd_code: int = 29
    ) -> RefreshResult:
        result = RefreshResult(source="data.gov.in/LGD")
        records = await self._client.fetch_all_records(
            LGD_DISTRICTS_RESOURCE,
            filters={"state_code": str(state_lgd_code)},
        )
        result.records_fetched = len(records)

        existing = (
            await db.execute(
                select(District).where(District.state_lgd_code == state_lgd_code)
            )
        ).scalars().all()
        existing_by_code = {d.lgd_code: d for d in existing}

        for rec in records:
            code = int(rec.get("district_code", 0))
            name = rec.get("district_name_english", "").strip()
            if not code or not name:
                continue

            if code in existing_by_code:
                district = existing_by_code[code]
                if district.name != name:
                    district.name = name
                    result.records_updated += 1
                else:
                    result.records_unchanged += 1
            else:
                db.add(
                    District(
                        lgd_code=code, name=name, state_lgd_code=state_lgd_code
                    )
                )
                result.records_inserted += 1

        await db.commit()
        return result.complete()
