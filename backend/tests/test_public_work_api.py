from uuid import uuid4

import pytest
from app.database.session import get_session
from app.main import app
from app.models import AccessEvent
from app.repositories.exhibition import create_exhibition
from app.repositories.work import create_work
from app.schemas.exhibition import ExhibitionCreate
from app.schemas.work import WorkCreate
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select


@pytest.mark.asyncio
async def test_get_public_work_endpoint_returns_active_work(db_session):
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
            title="Obra Pública",
            artist="Artista Teste",
            description="Descrição pública.",
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
            response = await client.get(f"/public/works/{work.public_slug}")

        assert response.status_code == 200

        body = response.json()

        assert body["title"] == "Obra Pública"
        assert body["artist"] == "Artista Teste"
        assert body["description"] == "Descrição pública."

        assert "id" not in body
        assert "exhibition_id" not in body
        assert "public_slug" not in body

    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_public_work_endpoint_returns_404_when_not_found(
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
            response = await client.get("/public/works/slug-inexistente")

        assert response.status_code == 404
        assert response.json() == {"detail": "Work not found"}

    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_public_work_endpoint_returns_404_when_work_is_inactive(
    db_session,
):
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
            title="Obra Inativa",
            description="Descrição.",
        ),
    )

    work.is_active = False
    await db_session.commit()

    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.get(f"/public/works/{work.public_slug}")

        assert response.status_code == 404
        assert response.json() == {"detail": "Work not found"}

    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_public_work_endpoint_returns_404_when_exhibition_is_inactive(
    db_session,
):
    exhibition = await create_exhibition(
        db_session,
        ExhibitionCreate(
            title="Exposição Inativa",
            description="Descrição.",
        ),
    )

    work = await create_work(
        db_session,
        WorkCreate(
            exhibition_id=exhibition.id,
            title="Obra Ativa",
            description="Descrição.",
        ),
    )

    exhibition.is_active = False
    await db_session.commit()

    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.get(f"/public/works/{work.public_slug}")

        assert response.status_code == 404
        assert response.json() == {"detail": "Work not found"}

    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_register_public_work_access_creates_event(db_session):
    exhibition = await create_exhibition(
        db_session,
        ExhibitionCreate(
            title="Exposição Métricas",
            description="Exposição usada para teste de acesso.",
        ),
    )

    work = await create_work(
        db_session,
        WorkCreate(
            exhibition_id=exhibition.id,
            title="Obra Métricas",
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
            response = await client.post(f"/public/works/{work.public_slug}/access")

        assert response.status_code == 204
        assert response.content == b""

        result = await db_session.execute(
            select(AccessEvent).where(AccessEvent.work_id == work.id)
        )

        access_event = result.scalar_one_or_none()

        assert access_event is not None
        assert access_event.work_id == work.id

    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_register_public_work_access_returns_404_when_not_found(
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
            response = await client.post(f"/public/works/{uuid4()}/access")

        assert response.status_code == 404
        assert response.json() == {"detail": "Work not found"}

    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_register_public_work_access_returns_404_when_work_is_inactive(
    db_session,
):
    exhibition = await create_exhibition(
        db_session,
        ExhibitionCreate(
            title="Exposição Ativa",
            description="Exposição usada para teste.",
        ),
    )

    work = await create_work(
        db_session,
        WorkCreate(
            exhibition_id=exhibition.id,
            title="Obra Inativa",
            description="Descrição da obra.",
        ),
    )

    work.is_active = False
    await db_session.commit()

    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.post(f"/public/works/{work.public_slug}/access")

        assert response.status_code == 404
        assert response.json() == {"detail": "Work not found"}

    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_register_public_work_access_returns_404_when_exhibition_is_inactive(
    db_session,
):
    exhibition = await create_exhibition(
        db_session,
        ExhibitionCreate(
            title="Exposição Inativa",
            description="Exposição usada para teste.",
        ),
    )

    work = await create_work(
        db_session,
        WorkCreate(
            exhibition_id=exhibition.id,
            title="Obra Ativa",
            description="Descrição da obra.",
        ),
    )

    exhibition.is_active = False
    await db_session.commit()

    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.post(f"/public/works/{work.public_slug}/access")

        assert response.status_code == 404
        assert response.json() == {"detail": "Work not found"}

    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_public_work_audio_returns_mp3(
    db_session,
):
    from io import BytesIO
    from unittest.mock import MagicMock

    from app.core.storage import get_storage_service

    exhibition = await create_exhibition(
        db_session,
        ExhibitionCreate(
            title="Exposição com Áudio",
            description="Exposição pública com áudio.",
        ),
    )

    work = await create_work(
        db_session,
        WorkCreate(
            exhibition_id=exhibition.id,
            title="Obra com Áudio",
            description="Descrição da obra.",
            audio_url=f"works/test/audio/audio.mp3",
        ),
    )

    storage = MagicMock()
    storage.download.return_value = BytesIO(b"fake mp3 content")

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
            response = await client.get(f"/public/works/{work.public_slug}/media/audio")

        assert response.status_code == 200
        assert response.headers["content-type"] == "audio/mpeg"
        assert response.content == b"fake mp3 content"

        storage.download.assert_called_once_with(
            object_key="works/test/audio/audio.mp3"
        )

    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_public_work_audio_returns_404_when_work_has_no_audio(
    db_session,
):
    from unittest.mock import MagicMock

    from app.core.storage import get_storage_service

    exhibition = await create_exhibition(
        db_session,
        ExhibitionCreate(
            title="Exposição sem Áudio",
            description="Exposição usada para testar obra sem áudio.",
        ),
    )

    work = await create_work(
        db_session,
        WorkCreate(
            exhibition_id=exhibition.id,
            title="Obra sem Áudio",
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
            response = await client.get(f"/public/works/{work.public_slug}/media/audio")

        assert response.status_code == 404
        assert response.json() == {"detail": "Audio not found"}

        storage.download.assert_not_called()

    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_public_work_audio_returns_404_when_work_not_found(
    db_session,
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
            response = await client.get("/public/works/slug-que-nao-existe/media/audio")

        assert response.status_code == 404
        assert response.json() == {"detail": "Work not found"}

        storage.download.assert_not_called()

    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_public_work_audio_returns_500_when_storage_fails(
    db_session,
):
    from unittest.mock import MagicMock

    from app.core.storage import get_storage_service

    exhibition = await create_exhibition(
        db_session,
        ExhibitionCreate(
            title="Exposição Storage Error",
            description="Exposição usada para testar falha no storage.",
        ),
    )

    work = await create_work(
        db_session,
        WorkCreate(
            exhibition_id=exhibition.id,
            title="Obra Storage Error",
            description="Descrição da obra.",
            audio_url="works/test/audio/audio.mp3",
        ),
    )

    storage = MagicMock()
    storage.download.side_effect = RuntimeError("Storage unavailable")

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
            response = await client.get(f"/public/works/{work.public_slug}/media/audio")

        assert response.status_code == 500

        storage.download.assert_called_once_with(
            object_key="works/test/audio/audio.mp3"
        )

    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_public_work_audio_description_returns_mp3(
    db_session,
):
    from io import BytesIO
    from unittest.mock import MagicMock

    from app.core.storage import get_storage_service

    exhibition = await create_exhibition(
        db_session,
        ExhibitionCreate(
            title="Exposição com Audiodescrição",
            description="Exposição pública com audiodescrição.",
        ),
    )

    work = await create_work(
        db_session,
        WorkCreate(
            exhibition_id=exhibition.id,
            title="Obra com Audiodescrição",
            description="Descrição da obra.",
            audio_description_url=("works/test/audio-description/audio.mp3"),
        ),
    )

    storage = MagicMock()
    storage.download.return_value = BytesIO(b"fake audio description")

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
            response = await client.get(
                f"/public/works/{work.public_slug}/media/audio-description"
            )

        assert response.status_code == 200
        assert response.headers["content-type"] == "audio/mpeg"
        assert response.content == b"fake audio description"

        storage.download.assert_called_once_with(
            object_key=("works/test/audio-description/audio.mp3")
        )

    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_public_work_libras_video_returns_mp4(
    db_session,
):
    from io import BytesIO
    from unittest.mock import MagicMock

    from app.core.storage import get_storage_service

    exhibition = await create_exhibition(
        db_session,
        ExhibitionCreate(
            title="Exposição com Libras",
            description="Exposição pública com vídeo em Libras.",
        ),
    )

    work = await create_work(
        db_session,
        WorkCreate(
            exhibition_id=exhibition.id,
            title="Obra com Libras",
            description="Descrição da obra.",
            libras_video_url="works/test/libras/video.mp4",
        ),
    )

    storage = MagicMock()
    storage.download.return_value = BytesIO(b"fake mp4 content")

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
            response = await client.get(
                f"/public/works/{work.public_slug}/media/libras"
            )

        assert response.status_code == 200
        assert response.headers["content-type"] == "video/mp4"
        assert response.content == b"fake mp4 content"

        storage.download.assert_called_once_with(
            object_key="works/test/libras/video.mp4"
        )

    finally:
        app.dependency_overrides.clear()
