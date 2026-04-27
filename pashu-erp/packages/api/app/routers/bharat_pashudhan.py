"""Bharat Pashudhan national animal registry endpoints."""

from uuid import UUID

import httpx
from fastapi import APIRouter, Depends, HTTPException

from app.middleware.auth import get_current_user
from app.models.user import User
from app.schemas.bharat_pashudhan import RegistryAnimalLookup, RegistrySyncResponse
from app.services.bharat_pashudhan import (
    lookup_animal,
    sync_animal,
)

router = APIRouter(prefix="/v1/registry", tags=["Bharat Pashudhan"])


@router.get("/lookup/{pashu_aadhaar_id}", response_model=RegistryAnimalLookup)
async def lookup_from_registry(
    pashu_aadhaar_id: str, current_user: User = Depends(get_current_user)
):
    """Look up an animal from the national Bharat Pashudhan registry."""
    try:
        result = await lookup_animal(pashu_aadhaar_id)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"Registry lookup failed: {exc.response.text}",
        ) from exc

    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Animal with Pashu Aadhaar ID '{pashu_aadhaar_id}'"
            " not found in national registry",
        )
    return result


@router.post("/sync/{animal_id}", response_model=RegistrySyncResponse)
async def sync_with_registry(animal_id: UUID, current_user: User = Depends(get_current_user)):
    """Sync a local animal record with the national registry."""
    try:
        result = await sync_animal(animal_id)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"Registry sync failed: {exc.response.text}",
        ) from exc
    return result
