# app/routers/storage.py
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.middleware.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/v1/storage", tags=["Storage"])


class UploadUrlRequest(BaseModel):
    content_type: str = "image/jpeg"
    folder: str = "uploads"


class UploadUrlResponse(BaseModel):
    upload_url: str
    file_key: str
    expires_in: int


def _get_storage_service():
    import app.main as main_mod
    s3_service = getattr(main_mod.app.state, "s3_storage", None)
    if not s3_service:
        raise HTTPException(503, "Storage service not configured")
    return s3_service


@router.post("/upload-url", response_model=UploadUrlResponse, status_code=201)
async def get_upload_url(
    body: UploadUrlRequest,
    current_user: User = Depends(get_current_user),
):
    s3_service = _get_storage_service()
    try:
        result = await s3_service.get_upload_url(
            content_type=body.content_type,
            folder=f"{body.folder}/{current_user.id}",
        )
        return result
    except ValueError as e:
        raise HTTPException(400, str(e)) from None


@router.get("/download-url")
async def get_download_url(
    file_key: str = Query(...),
    current_user: User = Depends(get_current_user),
):
    s3_service = _get_storage_service()
    url = await s3_service.get_download_url(file_key)
    return {"download_url": url, "file_key": file_key}
