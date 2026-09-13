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
