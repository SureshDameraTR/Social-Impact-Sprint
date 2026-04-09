"""Bharat Pashudhan national animal registry endpoints."""

from uuid import UUID

import httpx
from fastapi import APIRouter, HTTPException

from app.services.bharat_pashudhan import (
    lookup_animal,
    sync_animal,
)

router = APIRouter(prefix="/v1/registry", tags=["Bharat Pashudhan"])


@router.get("/lookup/{pashu_aadhaar_id}")
async def lookup_from_registry(pashu_aadhaar_id: str):
    """Look up an animal from the national Bharat Pashudhan registry."""
    try:
        result = await lookup_animal(pashu_aadhaar_id)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"Registry lookup failed: {exc.response.text}",
        )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Animal with Pashu Aadhaar ID '{pashu_aadhaar_id}' not found in national registry",
        )
    return result


@router.post("/sync/{animal_id}")
async def sync_with_registry(animal_id: UUID):
    """Sync a local animal record with the national registry."""
    try:
        result = await sync_animal(animal_id)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"Registry sync failed: {exc.response.text}",
        )
    return result
