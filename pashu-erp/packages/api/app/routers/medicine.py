"""Medicine withdrawal tracking endpoints."""

from datetime import date, datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.animal import Animal
from app.models.medicine import Medicine, MedicineAdministration
from app.models.user import User
from app.schemas.medicine import MedicineAdministerRequest, MedicineRead, WithdrawalStatus

router = APIRouter(prefix="/v1/medicines", tags=["Medicines"])


@router.get("", response_model=list[MedicineRead])
async def list_medicines(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """List all medicines with withdrawal period information."""
    result = await db.execute(
        select(Medicine).order_by(Medicine.name_en).offset(skip).limit(limit)
    )
    return result.scalars().all()


@router.post("/administer", status_code=status.HTTP_201_CREATED)
async def administer_medicine(
    body: MedicineAdministerRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Administer a medicine and auto-calculate withdrawal dates."""
    # Verify animal ownership
    animal_result = await db.execute(select(Animal).where(Animal.id == body.animal_id))
    animal = animal_result.scalar_one_or_none()
    if animal is None:
        raise HTTPException(status_code=404, detail="Animal not found")
    if str(animal.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not your animal")

    # Get medicine details
    med_result = await db.execute(select(Medicine).where(Medicine.id == body.medicine_id))
    medicine = med_result.scalar_one_or_none()
    if medicine is None:
        raise HTTPException(status_code=404, detail="Medicine not found")

    administered_at = body.administered_at or datetime.now(timezone.utc)
    admin_date = administered_at.date() if isinstance(administered_at, datetime) else administered_at

    withdrawal_milk_until = (
        admin_date + timedelta(days=medicine.withdrawal_milk_days)
        if medicine.withdrawal_milk_days > 0 else None
    )
    withdrawal_meat_until = (
        admin_date + timedelta(days=medicine.withdrawal_meat_days)
        if medicine.withdrawal_meat_days > 0 else None
    )

    administration = MedicineAdministration(
        animal_id=str(body.animal_id),
        medicine_id=str(body.medicine_id),
        administered_at=administered_at,
        withdrawal_milk_until=withdrawal_milk_until,
        withdrawal_meat_until=withdrawal_meat_until,
    )
    db.add(administration)
    await db.commit()
    await db.refresh(administration)

    return {
        "id": str(administration.id),
        "animal_id": str(body.animal_id),
        "medicine": medicine.name_en,
        "administered_at": administered_at.isoformat(),
        "withdrawal_milk_until": withdrawal_milk_until.isoformat() if withdrawal_milk_until else None,
        "withdrawal_meat_until": withdrawal_meat_until.isoformat() if withdrawal_meat_until else None,
        "message": f"Medicine administered. {'Milk withdrawal until ' + withdrawal_milk_until.isoformat() + '.' if withdrawal_milk_until else 'No milk withdrawal required.'}",
    }


@router.get("/withdrawal-status/{animal_id}", response_model=WithdrawalStatus)
async def get_withdrawal_status(
    animal_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get current withdrawal status for an animal."""
    today = date.today()

    result = await db.execute(
        select(MedicineAdministration)
        .where(MedicineAdministration.animal_id == animal_id)
        .options(selectinload(MedicineAdministration.medicine))
        .order_by(MedicineAdministration.administered_at.desc())
    )
    administrations = result.scalars().all()

    active_withdrawals = []
    latest_milk_date = None
    latest_meat_date = None

    for admin in administrations:
        milk_active = admin.withdrawal_milk_until and admin.withdrawal_milk_until > today
        meat_active = admin.withdrawal_meat_until and admin.withdrawal_meat_until > today

        if milk_active or meat_active:
            med = admin.medicine
            active_withdrawals.append({
                "medicine": med.name_en if med else "Unknown",
                "administered_at": admin.administered_at.isoformat(),
                "milk_withdrawal_until": admin.withdrawal_milk_until.isoformat() if milk_active else None,
                "meat_withdrawal_until": admin.withdrawal_meat_until.isoformat() if meat_active else None,
            })

            if milk_active and (latest_milk_date is None or admin.withdrawal_milk_until > latest_milk_date):
                latest_milk_date = admin.withdrawal_milk_until
            if meat_active and (latest_meat_date is None or admin.withdrawal_meat_until > latest_meat_date):
                latest_meat_date = admin.withdrawal_meat_until

    return WithdrawalStatus(
        animal_id=animal_id,
        active_withdrawals=active_withdrawals,
        milk_safe=latest_milk_date is None,
        meat_safe=latest_meat_date is None,
        earliest_milk_safe_date=latest_milk_date,
        earliest_meat_safe_date=latest_meat_date,
    )
