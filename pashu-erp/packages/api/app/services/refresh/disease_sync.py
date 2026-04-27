# app/services/refresh/disease_sync.py
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain_knowledge import DiseaseRule
from app.services.disease_rules import DISEASE_RULES
from app.services.refresh.base import RefreshResult

logger = logging.getLogger(__name__)


class DiseaseSyncService:
    async def seed_from_hardcoded(self, db: AsyncSession) -> RefreshResult:
        """Bootstrap: upsert DISEASE_RULES dict into the DB by (species_code, disease_name)."""
        result = RefreshResult(source="hardcoded/disease_rules.py")

        all_rules = []
        for species, rules in DISEASE_RULES.items():
            for rule in rules:
                all_rules.append((species, rule))

        result.records_fetched = len(all_rules)

        for species, rule in all_rules:
            existing = (await db.execute(
                select(DiseaseRule).where(
                    DiseaseRule.species_code == species,
                    DiseaseRule.disease_name == rule["disease"],
                )
            )).scalar_one_or_none()

            if existing:
                existing.symptoms = rule["symptoms"]
                existing.min_match = rule["min_match"]
                existing.risk_level = rule["risk_level"]
                existing.action = rule["action"]
                existing.source = rule.get("source", "")
                existing.is_active = True
                result.records_updated += 1
            else:
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
