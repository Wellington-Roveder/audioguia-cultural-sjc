from uuid import uuid4

import pytest
from app.database.session import get_session
from app.main import app
from app.repositories.access_event import create_access_event
from app.repositories.exhibition import create_exhibition
from app.repositories.work import create_work
from app.schemas.exhibition import ExhibitionCreate
from app.schemas.work import WorkCreate
from httpx import ASGITransport, AsyncClient


@pytest.mark.asyncio
async def test_get_work_metrics(db_session):
    exhibition = await create_exhibition(
        db_session,
        ExhibitionCreate(
            title="Exposição Métricas",
            description="Exposição para teste de métricas.",
        ),
    )

    work = await create_work(
        db_session,
        WorkCreate(
            exhibition_id=exhibition.id,
            title="Obra Métricas",
            description="Obra para teste de métricas.",
        ),
    )

    await create_access_event(db_session, work.id)
    await create_access_event(db_session, work.id)

    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.get(f"/metrics/works/{work.id}")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "work_id": str(work.id),
        "access_count": 2,
    }


@pytest.mark.asyncio
async def test_get_work_metrics_with_zero_accesses(db_session):
    exhibition = await create_exhibition(
        db_session,
        ExhibitionCreate(
            title="Exposição Sem Acessos",
            description="Exposição para teste.",
        ),
    )

    work = await create_work(
        db_session,
        WorkCreate(
            exhibition_id=exhibition.id,
            title="Obra Sem Acessos",
            description="Obra sem acessos.",
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
            response = await client.get(f"/metrics/works/{work.id}")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "work_id": str(work.id),
        "access_count": 0,
    }


@pytest.mark.asyncio
async def test_get_work_metrics_not_found(db_session):
    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.get(f"/metrics/works/{uuid4()}")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Work not found",
    }


@pytest.mark.asyncio
async def test_get_exhibition_metrics(db_session):
    exhibition = await create_exhibition(
        db_session,
        ExhibitionCreate(
            title="Exposição Agregada",
            description="Exposição para teste agregado.",
        ),
    )

    work_one = await create_work(
        db_session,
        WorkCreate(
            exhibition_id=exhibition.id,
            title="Obra Um",
            description="Primeira obra.",
        ),
    )

    work_two = await create_work(
        db_session,
        WorkCreate(
            exhibition_id=exhibition.id,
            title="Obra Dois",
            description="Segunda obra.",
        ),
    )

    await create_access_event(db_session, work_one.id)
    await create_access_event(db_session, work_one.id)
    await create_access_event(db_session, work_two.id)

    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.get(f"/metrics/exhibitions/{exhibition.id}")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "exhibition_id": str(exhibition.id),
        "access_count": 3,
    }


@pytest.mark.asyncio
async def test_get_exhibition_metrics_with_zero_accesses(db_session):
    exhibition = await create_exhibition(
        db_session,
        ExhibitionCreate(
            title="Exposição Sem Métricas",
            description="Exposição sem eventos de acesso.",
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
            response = await client.get(f"/metrics/exhibitions/{exhibition.id}")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "exhibition_id": str(exhibition.id),
        "access_count": 0,
    }


@pytest.mark.asyncio
async def test_get_exhibition_metrics_not_found(db_session):
    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.get(f"/metrics/exhibitions/{uuid4()}")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Exhibition not found",
    }
