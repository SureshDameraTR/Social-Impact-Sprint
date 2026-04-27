"""Mock file storage service for insurance photo uploads."""

from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

router = APIRouter(prefix="/api/v1/storage", tags=["Storage"])

UPLOAD_DIR = Path(__file__).parent.parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png"}
EXTENSION_MAP = {"image/jpeg": ".jpg", "image/png": ".png"}

# In-memory metadata store (resets on restart — acceptable for a mock service)
_file_store: dict[str, dict] = {}


@router.post("/files")
async def upload_file(
    file: UploadFile = File(...),
    category: str = Form("general"),
    entity_type: Optional[str] = Form(None),
    entity_id: Optional[str] = Form(None),
):
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported content type '{file.content_type}'. Allowed: image/jpeg, image/png",
        )

    file_id = str(uuid4())
    extension = EXTENSION_MAP[file.content_type]
    stored_name = f"{file_id}{extension}"
    stored_path = UPLOAD_DIR / stored_name

    MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10MB
    contents = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(contents) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File exceeds 10MB limit")
    stored_path.write_bytes(contents)

    metadata = {
        "file_id": file_id,
        "url": f"/api/v1/storage/files/{file_id}",
        "filename": file.filename or "unknown",
        "content_type": file.content_type,
        "size_bytes": len(contents),
        "category": category,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "_stored_path": str(stored_path),
    }
    _file_store[file_id] = metadata

    # Return metadata without internal fields
    return {k: v for k, v in metadata.items() if not k.startswith("_")}


@router.get("/files")
async def list_files(
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
):
    results = list(_file_store.values())

    if entity_type is not None:
        results = [f for f in results if f.get("entity_type") == entity_type]
    if entity_id is not None:
        results = [f for f in results if f.get("entity_id") == entity_id]

    public = [{k: v for k, v in f.items() if not k.startswith("_")} for f in results]
    return {"data": public, "total": len(public)}


@router.get("/files/{file_id}")
async def get_file(file_id: str):
    metadata = _file_store.get(file_id)
    if metadata is None:
        raise HTTPException(status_code=404, detail="File not found")

    stored_path = Path(metadata["_stored_path"]).resolve()
    if not stored_path.is_relative_to(UPLOAD_DIR.resolve()):
        raise HTTPException(status_code=403, detail="Access denied")
    if not stored_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")

    return FileResponse(
        path=stored_path,
        media_type=metadata["content_type"],
        filename=metadata["filename"],
    )
