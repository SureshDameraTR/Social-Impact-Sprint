"""User profile endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user, require_admin
from app.models.animal import Animal
from app.models.user import User
from app.schemas.users import FarmerListResponse, UserProfile

router = APIRouter(prefix="/v1", tags=["Users"])


@router.get("/farmers", response_model=FarmerListResponse)
async def list_farmers(
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """List all farmers with animal counts (for admin dashboard)."""
    base = select(User).where(User.role == "farmer", User.deleted_at.is_(None))
    count_result = await db.execute(select(func.count()).select_from(base.subquery()))
    total = count_result.scalar() or 0

    result = await db.execute(
        base.order_by(User.created_at.desc()).offset(offset).limit(limit)
    )
    users = result.scalars().all()

    # Get animal counts in one query
    animal_counts_result = await db.execute(
        select(Animal.user_id, func.count().label("count"))
        .where(Animal.deleted_at.is_(None))
        .group_by(Animal.user_id)
    )
    animal_counts = {str(row.user_id): row.count for row in animal_counts_result.all()}

    data = []
    for u in users:
        data.append({
            "id": str(u.id),
            "name": u.name,
            "phone": u.phone,
            "district": u.location_district,
            "state": u.location_state,
            "village_code": u.village_code,
            "animals_count": animal_counts.get(str(u.id), 0),
            "registered_date": u.created_at.isoformat() if u.created_at else None,
        })

    return {"data": data, "total": total, "limit": limit, "offset": offset}


@router.get("/users/profile", response_model=UserProfile)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the authenticated user's profile with summary stats."""
    animal_count_result = await db.execute(
        select(func.count()).select_from(Animal).where(Animal.user_id == current_user.id, Animal.deleted_at.is_(None))
    )
    animal_count = animal_count_result.scalar() or 0

    return {
        "id": str(current_user.id),
        "name": current_user.name,
        "phone": current_user.phone,
        "role": current_user.role,
        "lang_pref": current_user.lang_pref,
        "location_district": current_user.location_district,
        "location_state": current_user.location_state,
        "village_code": current_user.village_code,
        "preferences": current_user.preferences,
        "animal_count": animal_count,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
    }
