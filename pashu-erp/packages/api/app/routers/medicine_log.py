"""Medicine log endpoints — aliases for mobile app compatibility.

The mobile app calls /v1/medicine-log/... while the canonical endpoints
live under /v1/medicines/... in medicine.py. This router provides the
alternative URL prefix.
"""

from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.animal import Animal
from app.models.medicine import MedicineAdministration
from app.models.user import User
from app.schemas.medicine_log import WithdrawalListResponse

router = APIRouter(prefix="/v1/medicine-log", tags=["Medicine Log"])


@router.get("/withdrawals", response_model=WithdrawalListResponse)
async def get_active_withdrawals(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get active medicine withdrawal statuses for all of the user's animals."""
    # Get user's animal IDs
    animal_result = await db.execute(
        select(Animal.id, Animal.name, Animal.species)
        .where(Animal.user_id == current_user.id, Animal.deleted_at.is_(None))
    )
    animals = animal_result.all()
    if not animals:
        return {"data": [], "total": 0}

    animal_ids = [a.id for a in animals]
    animal_map = {str(a.id): {"name": a.name, "species": a.species} for a in animals}

    today = date.today()

    result = await db.execute(
        select(MedicineAdministration)
        .where(MedicineAdministration.animal_id.in_(animal_ids), MedicineAdministration.deleted_at.is_(None))
        .options(selectinload(MedicineAdministration.medicine))
        .order_by(MedicineAdministration.administered_at.desc())
    )
    administrations = result.scalars().all()

    withdrawals = []
    for admin in administrations:
        milk_active = admin.withdrawal_milk_until and admin.withdrawal_milk_until > today
        meat_active = admin.withdrawal_meat_until and admin.withdrawal_meat_until > today
        if not (milk_active or meat_active):
            continue

        animal_info = animal_map.get(str(admin.animal_id), {})
        med = admin.medicine
        withdrawals.append({
            "animal_id": str(admin.animal_id),
            "animal_name": animal_info.get("name"),
            "species": animal_info.get("species"),
            "medicine": med.name_en if med else "Unknown",
            "administered_at": admin.administered_at.isoformat(),
            "milk_withdrawal_until": admin.withdrawal_milk_until.isoformat() if milk_active else None,
            "meat_withdrawal_until": admin.withdrawal_meat_until.isoformat() if meat_active else None,
            "milk_safe": not milk_active,
            "meat_safe": not meat_active,
        })

    return {"data": withdrawals, "total": len(withdrawals)}
