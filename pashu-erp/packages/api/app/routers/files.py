"""File upload and download proxy endpoints."""

import logging

import httpx
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import Response

from app.middleware.auth import get_current_user
from app.models.user import User
from app.services import storage_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/files", tags=["Files"])


@router.post("")
async def upload_file(
    file: UploadFile = File(...),
    category: str = Form(...),
    entity_type: str = Form(...),
    entity_id: str = Form(...),
    current_user: User = Depends(get_current_user),
):
    """Upload a file to the storage backend."""
    try:
        file_bytes = await file.read()
        return await storage_service.upload_file(
            file_bytes=file_bytes,
            filename=file.filename or "upload",
            content_type=file.content_type or "application/octet-stream",
            category=category,
            entity_type=entity_type,
            entity_id=entity_id,
        )
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail="Storage backend error")
    except httpx.RequestError:
        logger.exception("Storage service request failed")
        raise HTTPException(status_code=502, detail="Storage service unavailable")


@router.get("/{file_id}")
async def get_file(
    file_id: str,
    current_user: User = Depends(get_current_user),
):
    """Download a file from the storage backend."""
    try:
        file_bytes, content_type = await storage_service.get_file(file_id)
        return Response(content=file_bytes, media_type=content_type)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail="Storage backend error")
    except httpx.RequestError:
        logger.exception("Storage service request failed")
        raise HTTPException(status_code=502, detail="Storage service unavailable")


@router.get("")
async def list_files(
    entity_type: str = Query(None, description="Filter by entity type"),
    entity_id: str = Query(None, description="Filter by entity ID"),
    current_user: User = Depends(get_current_user),
):
    """List files with optional entity filters."""
    try:
        return await storage_service.list_files(
            entity_type=entity_type,
            entity_id=entity_id,
        )
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail="Storage backend error")
    except httpx.RequestError:
        logger.exception("Storage service request failed")
        raise HTTPException(status_code=502, detail="Storage service unavailable")
