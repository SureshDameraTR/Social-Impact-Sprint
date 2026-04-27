"""File upload and download proxy endpoints."""

import logging

import httpx
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import Response

from app.middleware.auth import get_current_user
from app.models.user import User
from app.schemas.files import FileListResponse, FileUploadResponse
from app.services import storage_service

logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "application/pdf"}

# Magic bytes for common image/document types
MAGIC_BYTES = {
    b"\xff\xd8\xff": "image/jpeg",
    b"\x89PNG": "image/png",
    b"GIF8": "image/gif",
    b"%PDF": "application/pdf",
}

router = APIRouter(prefix="/v1/files", tags=["Files"])


@router.post("", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    category: str = Form(...),
    entity_type: str = Form(...),
    entity_id: str = Form(...),
    current_user: User = Depends(get_current_user),
):
    """Upload a file to the storage backend."""
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{file.content_type}' not allowed. "
            f"Accepted: {', '.join(sorted(ALLOWED_CONTENT_TYPES))}",
        )
    # Validate actual file content via magic bytes
    header = await file.read(8)
    await file.seek(0)
    if not any(header.startswith(magic) for magic in MAGIC_BYTES):
        raise HTTPException(
            status_code=400,
            detail="File content does not match allowed types",
        )
    try:
        file_bytes = await file.read()
        if len(file_bytes) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large ({len(file_bytes)} bytes). "
                f"Maximum size: {MAX_FILE_SIZE} bytes (10MB)",
            )
        return await storage_service.upload_file(
            file_bytes=file_bytes,
            filename=file.filename or "upload",
            content_type=file.content_type or "application/octet-stream",
            category=category,
            entity_type=entity_type,
            entity_id=entity_id,
        )
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code, detail="Storage backend error"
        ) from exc
    except httpx.RequestError:
        logger.exception("Storage service request failed")
        raise HTTPException(status_code=502, detail="Storage service unavailable") from None


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
        raise HTTPException(
            status_code=exc.response.status_code, detail="Storage backend error"
        ) from exc
    except httpx.RequestError:
        logger.exception("Storage service request failed")
        raise HTTPException(status_code=502, detail="Storage service unavailable") from None


@router.get("", response_model=FileListResponse)
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
        raise HTTPException(
            status_code=exc.response.status_code, detail="Storage backend error"
        ) from exc
    except httpx.RequestError:
        logger.exception("Storage service request failed")
        raise HTTPException(status_code=502, detail="Storage service unavailable") from None
