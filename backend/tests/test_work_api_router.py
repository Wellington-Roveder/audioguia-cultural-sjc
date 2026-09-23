from uuid import uuid4

import pytest
from app.database.session import get_session
from app.main import app
from app.repositories.exhibition import create_exhibition
from app.repositories.work import create_work, get_work_by_id
from app.schemas.exhibition import ExhibitionCreate
from app.schemas.work import WorkCreate
from httpx import ASGITransport, AsyncClient


@pytest.mark.asyncio
async def test_create_work_endpoint_creates_work(db_session, auth_headers):
    exhibition = await create_exhibition(
        db_session,
        ExhibitionCreate(
            title="Exposição Teste",
            description="Exposição usada pelo endpoint de obra.",
        ),
    )

    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.post(
                "/works",
                json={
                    "exhibition_id": str(exhibition.id),
                    "title": "Memórias do Vale",
                    "artist": "Artista Teste",
                    "description": "Descrição da obra.",
                },
                headers=auth_headers,
            )

        assert response.status_code == 201

        body = response.json()

        assert body["id"] is not None
        assert body["exhibition_id"] == str(exhibition.id)
        assert body["title"] == "Memórias do Vale"
        assert body["artist"] == "Artista Teste"
        assert body["description"] == "Descrição da obra."
        assert body["public_slug"]
        assert body["is_active"] is True

    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_work_endpoint_returns_404_when_exhibition_not_found(
    db_session, auth_headers
):
    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.post(
                "/works",
                json={
                    "exhibition_id": str(uuid4()),
                    "title": "Obra Teste",
                    "description": "Descrição.",
                },
                headers=auth_headers,
            )

        assert response.status_code == 404
        assert response.json() == {"detail": "Exhibition not found"}

    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_work_endpoint_returns_work(db_session, auth_headers):
    exhibition = await create_exhibition(
        db_session,
        ExhibitionCreate(
            title="Exposição Teste",
            description="Descrição.",
        ),
    )

    work = await create_work(
        db_session,
        WorkCreate(
            exhibition_id=exhibition.id,
            title="Obra para Busca",
            description="Descrição da obra.",
        ),
    )

    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.get(
                f"/works/{work.id}",
                headers=auth_headers,
            )

        assert response.status_code == 200

        body = response.json()

        assert body["id"] == str(work.id)
        assert body["exhibition_id"] == str(exhibition.id)
        assert body["title"] == "Obra para Busca"

    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_work_endpoint_returns_404_when_not_found(db_session, auth_headers):
    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.get(
                f"/works/{uuid4()}",
                headers=auth_headers,
            )

        assert response.status_code == 404
        assert response.json() == {"detail": "Work not found"}

    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_list_works_by_exhibition_endpoint_returns_related_works(
    db_session, auth_headers
):
    exhibition = await create_exhibition(
        db_session,
        ExhibitionCreate(
            title="Exposição Teste",
            description="Descrição.",
        ),
    )

    await create_work(
        db_session,
        WorkCreate(
            exhibition_id=exhibition.id,
            title="Obra A",
            description="Descrição A.",
        ),
    )

    await create_work(
        db_session,
        WorkCreate(
            exhibition_id=exhibition.id,
            title="Obra B",
            description="Descrição B.",
        ),
    )

    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.get(
                f"/works/by-exhibition/{exhibition.id}",
                headers=auth_headers,
            )

        assert response.status_code == 200

        body = response.json()

        assert len(body) == 2
        assert {item["title"] for item in body} == {
            "Obra A",
            "Obra B",
        }

    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_list_works_by_exhibition_endpoint_returns_404_when_exhibition_not_found(
    db_session, auth_headers
):
    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.get(
                f"/works/by-exhibition/{uuid4()}",
                headers=auth_headers,
            )

        assert response.status_code == 404
        assert response.json() == {"detail": "Exhibition not found"}

    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_update_work_endpoint_updates_work(db_session, auth_headers):
    exhibition = await create_exhibition(
        db_session,
        ExhibitionCreate(
            title="Exposição Teste",
            description="Descrição.",
        ),
    )

    work = await create_work(
        db_session,
        WorkCreate(
            exhibition_id=exhibition.id,
            title="Título Antigo",
            artist="Artista Antigo",
            description="Descrição antiga.",
        ),
    )

    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.patch(
                f"/works/{work.id}",
                json={
                    "title": "Título Atualizado",
                },
                headers=auth_headers,
            )

        assert response.status_code == 200

        body = response.json()

        assert body["id"] == str(work.id)
        assert body["title"] == "Título Atualizado"
        assert body["artist"] == "Artista Antigo"
        assert body["description"] == "Descrição antiga."

    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_update_work_endpoint_returns_404_when_not_found(
    db_session, auth_headers
):
    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.patch(
                f"/works/{uuid4()}",
                json={
                    "title": "Título Atualizado",
                },
                headers=auth_headers,
            )

        assert response.status_code == 404
        assert response.json() == {"detail": "Work not found"}

    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_delete_work_endpoint_removes_work(db_session, auth_headers):
    exhibition = await create_exhibition(
        db_session,
        ExhibitionCreate(
            title="Exposição Teste",
            description="Descrição.",
        ),
    )

    work = await create_work(
        db_session,
        WorkCreate(
            exhibition_id=exhibition.id,
            title="Obra para Exclusão",
            description="Descrição.",
        ),
    )

    work_id = work.id

    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.delete(
                f"/works/{work_id}",
                headers=auth_headers,
            )

        assert response.status_code == 204
        assert response.content == b""

        found_work = await get_work_by_id(
            db_session,
            work_id,
        )

        assert found_work is None

    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_delete_work_endpoint_returns_404_when_not_found(
    db_session, auth_headers
):
    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.delete(
                f"/works/{uuid4()}",
                headers=auth_headers,
            )

        assert response.status_code == 404
        assert response.json() == {"detail": "Work not found"}

    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_work_qr_endpoint_returns_png(db_session, auth_headers):
    exhibition = await create_exhibition(
        db_session,
        ExhibitionCreate(
            title="Exposição Teste QR",
            description="Exposição usada para testar QR Code.",
        ),
    )

    work = await create_work(
        db_session,
        WorkCreate(
            exhibition_id=exhibition.id,
            title="Obra com QR",
            description="Descrição da obra.",
        ),
    )

    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.get(
                f"/works/{work.id}/qr",
                headers=auth_headers,
            )

        assert response.status_code == 200
        assert response.headers["content-type"] == "image/png"
        assert response.content.startswith(b"\x89PNG\r\n\x1a\n")

        content_disposition = response.headers.get("content-disposition")

        assert content_disposition is not None
        assert f"qr-{work.public_slug}.png" in content_disposition

    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_work_qr_endpoint_returns_404_when_not_found(
    db_session, auth_headers
):
    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.get(
                f"/works/{uuid4()}/qr",
                headers=auth_headers,
            )

        assert response.status_code == 404
        assert response.json() == {"detail": "Work not found"}

    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_works_requires_authentication(
    db_session,
):
    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.get(
                f"/works/{uuid4()}",
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_upload_work_audio_stores_file_and_updates_work(
    db_session,
    auth_headers,
):
    from unittest.mock import MagicMock

    from app.core.storage import get_storage_service

    exhibition = await create_exhibition(
        db_session,
        ExhibitionCreate(
            title="Exposição com Áudio",
            description="Exposição usada para testar upload.",
        ),
    )

    work = await create_work(
        db_session,
        WorkCreate(
            exhibition_id=exhibition.id,
            title="Obra com Áudio",
            description="Descrição da obra.",
        ),
    )

    storage = MagicMock()

    async def override_get_session():
        yield db_session

    def override_get_storage_service():
        return storage

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_storage_service] = override_get_storage_service

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.post(
                f"/works/{work.id}/media/audio",
                files={
                    "file": (
                        "audio.mp3",
                        b"ID3\x04\x00\x00\x00\x00\x00\x00fake audio data",
                        "audio/mpeg",
                    )
                },
                headers=auth_headers,
            )

        assert response.status_code == 201

        storage.upload.assert_called_once()

        upload_call = storage.upload.call_args.kwargs

        assert upload_call["content_type"] == "audio/mpeg"
        assert str(work.id) in upload_call["object_key"]
        assert upload_call["object_key"].endswith(".mp3")

        await db_session.refresh(work)

        assert work.audio_url is not None

    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_upload_work_audio_rejects_non_mp3_file(
    db_session,
    auth_headers,
):
    from unittest.mock import MagicMock

    from app.core.storage import get_storage_service

    exhibition = await create_exhibition(
        db_session,
        ExhibitionCreate(
            title="Exposição com Áudio Inválido",
            description="Exposição usada para testar validação de mídia.",
        ),
    )

    work = await create_work(
        db_session,
        WorkCreate(
            exhibition_id=exhibition.id,
            title="Obra com Áudio Inválido",
            description="Descrição da obra.",
        ),
    )

    storage = MagicMock()

    async def override_get_session():
        yield db_session

    def override_get_storage_service():
        return storage

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_storage_service] = override_get_storage_service

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.post(
                f"/works/{work.id}/media/audio",
                files={
                    "file": (
                        "documento.pdf",
                        b"fake pdf content",
                        "application/pdf",
                    )
                },
                headers=auth_headers,
            )

        assert response.status_code == 415
        assert response.json() == {"detail": "Only MP3 audio files are allowed"}

        storage.upload.assert_not_called()

        await db_session.refresh(work)
        assert work.audio_url is None

    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_upload_work_audio_does_not_update_work_when_storage_fails(
    db_session,
    auth_headers,
):
    from unittest.mock import MagicMock

    from app.core.storage import get_storage_service

    exhibition = await create_exhibition(
        db_session,
        ExhibitionCreate(
            title="Exposição Storage Failure",
            description="Exposição usada para testar falha no storage.",
        ),
    )

    work = await create_work(
        db_session,
        WorkCreate(
            exhibition_id=exhibition.id,
            title="Obra Storage Failure",
            description="Descrição da obra.",
        ),
    )

    storage = MagicMock()
    storage.upload.side_effect = RuntimeError("Storage unavailable")

    async def override_get_session():
        yield db_session

    def override_get_storage_service():
        return storage

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_storage_service] = override_get_storage_service

    try:
        async with AsyncClient(
            transport=ASGITransport(
                app=app,
                raise_app_exceptions=False,
            ),
            base_url="http://test",
        ) as client:
            response = await client.post(
                f"/works/{work.id}/media/audio",
                files={
                    "file": (
                        "audio.mp3",
                        b"ID3\x04\x00\x00\x00\x00\x00\x00fake audio data",
                        "audio/mpeg",
                    )
                },
                headers=auth_headers,
            )

        assert response.status_code == 500

        await db_session.refresh(work)

        assert work.audio_url is None

    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_upload_work_audio_returns_404_without_calling_storage_when_work_not_found(
    db_session,
    auth_headers,
):
    from unittest.mock import MagicMock

    from app.core.storage import get_storage_service

    storage = MagicMock()

    async def override_get_session():
        yield db_session

    def override_get_storage_service():
        return storage

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_storage_service] = override_get_storage_service

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.post(
                f"/works/{uuid4()}/media/audio",
                files={
                    "file": (
                        "audio.mp3",
                        b"fake mp3 content",
                        "audio/mpeg",
                    )
                },
                headers=auth_headers,
            )

        assert response.status_code == 404
        assert response.json() == {"detail": "Work not found"}

        storage.upload.assert_not_called()

    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_upload_work_audio_rejects_invalid_mp3_content(
    db_session,
    auth_headers,
):
    from unittest.mock import MagicMock

    from app.core.storage import get_storage_service

    exhibition = await create_exhibition(
        db_session,
        ExhibitionCreate(
            title="Exposição MP3 Inválido",
            description="Exposição usada para validar conteúdo do arquivo.",
        ),
    )

    work = await create_work(
        db_session,
        WorkCreate(
            exhibition_id=exhibition.id,
            title="Obra MP3 Inválido",
            description="Descrição da obra.",
        ),
    )

    storage = MagicMock()

    async def override_get_session():
        yield db_session

    def override_get_storage_service():
        return storage

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_storage_service] = override_get_storage_service

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.post(
                f"/works/{work.id}/media/audio",
                files={
                    "file": (
                        "audio.mp3",
                        b"this is definitely not an mp3",
                        "audio/mpeg",
                    )
                },
                headers=auth_headers,
            )

        assert response.status_code == 415
        assert response.json() == {"detail": "Invalid MP3 file"}

        storage.upload.assert_not_called()

        await db_session.refresh(work)
        assert work.audio_url is None

    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_upload_work_audio_rejects_file_larger_than_10_mb(
    db_session,
    auth_headers,
):
    from unittest.mock import MagicMock

    from app.core.storage import get_storage_service

    exhibition = await create_exhibition(
        db_session,
        ExhibitionCreate(
            title="Exposição Áudio Grande",
            description="Exposição usada para testar limite de upload.",
        ),
    )

    work = await create_work(
        db_session,
        WorkCreate(
            exhibition_id=exhibition.id,
            title="Obra Áudio Grande",
            description="Descrição da obra.",
        ),
    )

    storage = MagicMock()

    async def override_get_session():
        yield db_session

    def override_get_storage_service():
        return storage

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_storage_service] = override_get_storage_service

    try:
        large_mp3 = b"ID3" + b"\x00" * (10 * 1024 * 1024)

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.post(
                f"/works/{work.id}/media/audio",
                files={
                    "file": (
                        "audio.mp3",
                        large_mp3,
                        "audio/mpeg",
                    )
                },
                headers=auth_headers,
            )

        assert response.status_code == 413
        assert response.json() == {"detail": "Audio file exceeds the 10 MB limit"}

        storage.upload.assert_not_called()

        await db_session.refresh(work)
        assert work.audio_url is None

    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_upload_work_audio_description_stores_file_and_updates_work(
    db_session,
    auth_headers,
):
    from unittest.mock import MagicMock

    from app.core.storage import get_storage_service

    exhibition = await create_exhibition(
        db_session,
        ExhibitionCreate(
            title="Exposição Audiodescrição",
            description="Exposição usada para testar audiodescrição.",
        ),
    )

    work = await create_work(
        db_session,
        WorkCreate(
            exhibition_id=exhibition.id,
            title="Obra com Audiodescrição",
            description="Descrição da obra.",
        ),
    )

    storage = MagicMock()

    async def override_get_session():
        yield db_session

    def override_get_storage_service():
        return storage

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_storage_service] = override_get_storage_service

    try:
        mp3_content = b"ID3\x04\x00\x00\x00\x00\x00\x00fake audio description"

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.post(
                f"/works/{work.id}/media/audio-description",
                files={
                    "file": (
                        "audiodescricao.mp3",
                        mp3_content,
                        "audio/mpeg",
                    )
                },
                headers=auth_headers,
            )

        assert response.status_code == 201

        storage.upload.assert_called_once()

        upload_call = storage.upload.call_args.kwargs

        assert upload_call["content_type"] == "audio/mpeg"
        assert str(work.id) in upload_call["object_key"]
        assert "audio-description" in upload_call["object_key"]
        assert upload_call["object_key"].endswith(".mp3")

        await db_session.refresh(work)

        assert work.audio_description_url is not None

    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_upload_work_libras_video_stores_file_and_updates_work(
    db_session,
    auth_headers,
):
    from unittest.mock import MagicMock

    from app.core.storage import get_storage_service

    exhibition = await create_exhibition(
        db_session,
        ExhibitionCreate(
            title="Exposição Libras",
            description="Exposição usada para testar vídeo em Libras.",
        ),
    )

    work = await create_work(
        db_session,
        WorkCreate(
            exhibition_id=exhibition.id,
            title="Obra com Libras",
            description="Descrição da obra.",
        ),
    )

    storage = MagicMock()

    async def override_get_session():
        yield db_session

    def override_get_storage_service():
        return storage

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_storage_service] = override_get_storage_service

    try:
        # Assinatura mínima compatível com container MP4:
        # size + "ftyp"
        mp4_content = (
            b"\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00mp42isomfake video content"
        )

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.post(
                f"/works/{work.id}/media/libras",
                files={
                    "file": (
                        "libras.mp4",
                        mp4_content,
                        "video/mp4",
                    )
                },
                headers=auth_headers,
            )

        print(response.status_code)
        print(response.json())
        assert response.status_code == 201

        storage.upload.assert_called_once()

        upload_call = storage.upload.call_args.kwargs

        assert upload_call["content_type"] == "video/mp4"
        assert str(work.id) in upload_call["object_key"]
        assert "libras" in upload_call["object_key"]
        assert upload_call["object_key"].endswith(".mp4")

        await db_session.refresh(work)

        assert work.libras_video_url is not None

    finally:
        app.dependency_overrides.clear()
