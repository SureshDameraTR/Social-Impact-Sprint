# app/services/storage_service.py
import logging
import uuid

logger = logging.getLogger(__name__)

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "application/pdf"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


class S3StorageService:
    def __init__(self, s3_client, bucket: str, presigned_expiry: int = 3600):
        self._s3 = s3_client
        self._bucket = bucket
        self._expiry = presigned_expiry

    async def get_upload_url(
        self,
        file_key: str | None = None,
        content_type: str = "image/jpeg",
        folder: str = "uploads",
    ) -> dict:
        if content_type not in ALLOWED_CONTENT_TYPES:
            raise ValueError(f"Content type {content_type} not allowed")

        if not file_key:
            ext = content_type.split("/")[-1]
            file_key = f"{folder}/{uuid.uuid4()}.{ext}"

        url = await self._s3.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": self._bucket,
                "Key": file_key,
                "ContentType": content_type,
            },
            ExpiresIn=self._expiry,
        )
        return {"upload_url": url, "file_key": file_key, "expires_in": self._expiry}

    async def get_download_url(self, file_key: str) -> str:
        return await self._s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": self._bucket, "Key": file_key},
            ExpiresIn=self._expiry,
        )

    async def delete_file(self, file_key: str) -> None:
        await self._s3.delete_object(Bucket=self._bucket, Key=file_key)
