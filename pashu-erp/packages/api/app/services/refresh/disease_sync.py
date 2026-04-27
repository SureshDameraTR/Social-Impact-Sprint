# app/services/refresh/disease_sync.py
import logging

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain_knowledge import DiseaseRule
from app.services.disease_rules import DISEASE_RULES
from app.services.refresh.base import RefreshResult

logger = logging.getLogger(__name__)


class DiseaseSyncService:
    async def seed_from_hardcoded(self, db: AsyncSession) -> RefreshResult:
        """One-time bootstrap: load existing DISEASE_RULES dict into the DB."""
        result = RefreshResult(source="hardcoded/disease_rules.py")

        count = (await db.execute(
            select(func.count()).select_from(DiseaseRule)
        )).scalar() or 0

        all_rules = []
        for species, rules in DISEASE_RULES.items():
            for rule in rules:
                all_rules.append((species, rule))

        result.records_fetched = len(all_rules)

        if count >= len(all_rules):
            result.records_unchanged = count
            return result.complete()

        for species, rule in all_rules:
            db.add(DiseaseRule(
                species_code=species,
                disease_name=rule["disease"],
                symptoms=rule["symptoms"],
                min_match=rule["min_match"],
                risk_level=rule["risk_level"],
                action=rule["action"],
                source=rule.get("source", ""),
            ))
            result.records_inserted += 1

        await db.commit()
        return result.complete()
