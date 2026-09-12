import pytest
from httpx import ASGITransport, AsyncClient

from app.database.session import get_session
from app.main import app
from app.repositories.exhibition import create_exhibition
from app.repositories.work import create_work
from app.schemas.exhibition import ExhibitionCreate
from app.schemas.work import WorkCreate


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
