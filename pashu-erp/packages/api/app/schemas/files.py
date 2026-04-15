"""Pydantic schemas for file upload/download endpoints."""

from pydantic import BaseModel


class FileUploadResponse(BaseModel):
    file_id: str
    url: str
    filename: str
    content_type: str
    size_bytes: int
    category: str
    entity_type: str | None = None
    entity_id: str | None = None
    created_at: str


class FileMetadata(BaseModel):
    file_id: str
    url: str
    filename: str
    content_type: str
    size_bytes: int
    category: str
    entity_type: str | None = None
    entity_id: str | None = None
    created_at: str


class FileListResponse(BaseModel):
    data: list[FileMetadata]
    total: int
