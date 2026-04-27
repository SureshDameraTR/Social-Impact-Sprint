# tests/test_storage_service.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.storage_service import S3StorageService


class TestS3StorageService:
    async def test_generate_upload_url(self):
        mock_s3 = AsyncMock()
        mock_s3.generate_presigned_url = AsyncMock(return_value="https://minio:9000/bucket/key?sig=abc")

        service = S3StorageService(s3_client=mock_s3, bucket="pashuraksha")
        result = await service.get_upload_url(file_key="animals/photo.jpg", content_type="image/jpeg")

        assert "minio" in result["upload_url"]
        assert result["file_key"] == "animals/photo.jpg"

    async def test_generate_download_url(self):
        mock_s3 = AsyncMock()
        mock_s3.generate_presigned_url = AsyncMock(return_value="https://minio:9000/bucket/key?sig=xyz")

        service = S3StorageService(s3_client=mock_s3, bucket="pashuraksha")
        result = await service.get_download_url(file_key="animals/photo.jpg")

        assert "minio" in result

    async def test_disallowed_content_type_raises(self):
        mock_s3 = AsyncMock()
        service = S3StorageService(s3_client=mock_s3, bucket="pashuraksha")

        with pytest.raises(ValueError, match="not allowed"):
            await service.get_upload_url(file_key="test.exe", content_type="application/x-msdownload")
