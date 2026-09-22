from io import BytesIO
from unittest.mock import MagicMock

from app.services.storage import StorageService


def test_upload_file_sends_object_to_storage():
    client = MagicMock()

    storage = StorageService(
        client=client,
        bucket_name="audioguia-cultural-sjc",
    )

    file_object = BytesIO(b"fake mp3 content")

    storage.upload(
        file_object=file_object,
        object_key="works/work-123/audio/audio.mp3",
        content_type="audio/mpeg",
    )

    client.upload_fileobj.assert_called_once_with(
        file_object,
        "audioguia-cultural-sjc",
        "works/work-123/audio/audio.mp3",
        ExtraArgs={"ContentType": "audio/mpeg"},
    )
