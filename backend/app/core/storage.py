import boto3
from app.core.config import settings
from app.services.storage import StorageService


def get_storage_service() -> StorageService:
    client = boto3.client(
        "s3",
        endpoint_url=settings.storage_endpoint_url,
        aws_access_key_id=settings.storage_access_key_id,
        aws_secret_access_key=settings.storage_secret_access_key,
        region_name="auto",
    )

    return StorageService(
        client=client,
        bucket_name=settings.storage_bucket_name,
    )
