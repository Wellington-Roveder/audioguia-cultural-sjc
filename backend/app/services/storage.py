from typing import BinaryIO, Protocol


class S3ClientProtocol(Protocol):
    def upload_fileobj(
        self,
        Fileobj: BinaryIO,
        Bucket: str,
        Key: str,
        ExtraArgs: dict[str, str] | None = None,
    ) -> None: ...

    def get_object(
        self,
        Bucket: str,
        Key: str,
    ) -> dict: ...


class StorageService:
    def __init__(
        self,
        client: S3ClientProtocol,
        bucket_name: str,
    ) -> None:
        self.client = client
        self.bucket_name = bucket_name

    def upload(
        self,
        file_object: BinaryIO,
        object_key: str,
        content_type: str,
    ) -> None:
        self.client.upload_fileobj(
            file_object,
            self.bucket_name,
            object_key,
            ExtraArgs={"ContentType": content_type},
        )

    def download(self, object_key: str) -> BinaryIO:
        response = self.client.get_object(
            Bucket=self.bucket_name,
            Key=object_key,
        )

        return response["Body"]
