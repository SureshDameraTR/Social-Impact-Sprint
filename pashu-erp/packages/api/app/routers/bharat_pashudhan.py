"""Bharat Pashudhan national animal registry endpoints."""

from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.services.bharat_pashudhan import lookup_animal, sync_animal

router = APIRouter(prefix="/v1/registry", tags=["Bharat Pashudhan"])


@router.get("/lookup/{pashu_aadhaar_id}")
async def lookup_from_registry(pashu_aadhaar_id: str):
    """Look up an animal from the national Bharat Pashudhan registry (mock)."""
    result = lookup_animal(pashu_aadhaar_id)
    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Animal with Pashu Aadhaar ID '{pashu_aadhaar_id}' not found in national registry",
        )
    return result


@router.post("/sync/{animal_id}")
async def sync_with_registry(animal_id: UUID):
    """Sync a local animal record with the national registry (mock)."""
    result = sync_animal(animal_id)
    return result
