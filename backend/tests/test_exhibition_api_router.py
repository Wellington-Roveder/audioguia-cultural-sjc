from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.database.session import get_session
from app.main import app
from app.repositories.exhibition import (
    create_exhibition,
    get_exhibition_by_id,
)
from app.schemas.exhibition import ExhibitionCreate


@pytest.mark.asyncio
async def test_create_exhibition_endpoint(
    db_session,
    auth_headers,
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
                "/exhibitions",
                json={
                    "title": "Exposição Cultural",
                    "description": "Exposição criada pelo teste da API.",
                },
                headers=auth_headers,
            )

        assert response.status_code == 201

        body = response.json()

        assert body["id"] is not None
        assert body["title"] == "Exposição Cultural"
        assert body["description"] == "Exposição criada pelo teste da API."
        assert body["start_date"] is None
        assert body["end_date"] is None
        assert body["is_active"] is True

    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_list_exhibitions_endpoint(
    db_session,
    auth_headers,
):
    await create_exhibition(
        db_session,
        ExhibitionCreate(
            title="Primeira Exposição",
            description="Primeira exposição da API.",
        ),
    )

    await create_exhibition(
        db_session,
        ExhibitionCreate(
            title="Segunda Exposição",
            description="Segunda exposição da API.",
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
                "/exhibitions",
                headers=auth_headers,
            )

        assert response.status_code == 200

        body = response.json()

        assert len(body) == 2
        assert {item["title"] for item in body} == {
            "Primeira Exposição",
            "Segunda Exposição",
        }

    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_exhibition_endpoint_returns_exhibition(
    db_session,
    auth_headers,
):
    created_exhibition = await create_exhibition(
        db_session,
        ExhibitionCreate(
            title="Exposição para Busca",
            description="Exposição criada para testar o endpoint.",
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
                f"/exhibitions/{created_exhibition.id}",
                headers=auth_headers,
            )

        assert response.status_code == 200

        body = response.json()

        assert body["id"] == str(created_exhibition.id)
        assert body["title"] == "Exposição para Busca"

    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_exhibition_endpoint_returns_404_when_not_found(
    db_session,
    auth_headers,
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
                f"/exhibitions/{uuid4()}",
                headers=auth_headers,
            )

        assert response.status_code == 404
        assert response.json() == {"detail": "Exhibition not found"}

    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_update_exhibition_endpoint_returns_404_when_not_found(
    db_session,
    auth_headers,
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
                f"/exhibitions/{uuid4()}",
                json={
                    "title": "Título Atualizado",
                },
                headers=auth_headers,
            )

        assert response.status_code == 404
        assert response.json() == {"detail": "Exhibition not found"}

    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_update_exhibition_endpoint_updates_exhibition(
    db_session,
    auth_headers,
):
    created_exhibition = await create_exhibition(
        db_session,
        ExhibitionCreate(
            title="Título Antigo",
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
                f"/exhibitions/{created_exhibition.id}",
                json={
                    "title": "Título Atualizado",
                },
                headers=auth_headers,
            )

        assert response.status_code == 200

        body = response.json()

        assert body["id"] == str(created_exhibition.id)
        assert body["title"] == "Título Atualizado"
        assert body["description"] == "Descrição antiga."

    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_delete_exhibition_endpoint_removes_exhibition(
    db_session,
    auth_headers,
):
    created_exhibition = await create_exhibition(
        db_session,
        ExhibitionCreate(
            title="Exposição para Exclusão",
            description="Será removida pela API.",
        ),
    )

    exhibition_id = created_exhibition.id

    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.delete(
                f"/exhibitions/{exhibition_id}",
                headers=auth_headers,
            )

        assert response.status_code == 204
        assert response.content == b""

        found_exhibition = await get_exhibition_by_id(
            db_session,
            exhibition_id,
        )

        assert found_exhibition is None

    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_delete_exhibition_endpoint_returns_404_when_not_found(
    db_session,
    auth_headers,
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
                f"/exhibitions/{uuid4()}",
                headers=auth_headers,
            )

        assert response.status_code == 404
        assert response.json() == {"detail": "Exhibition not found"}

    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_update_exhibition_endpoint_rejects_invalid_partial_date_range(
    db_session,
    auth_headers,
):
    created_exhibition = await create_exhibition(
        db_session,
        ExhibitionCreate(
            title="Exposição com Datas",
            description=("Exposição para testar atualização parcial de datas."),
            start_date="2026-10-01",
            end_date="2026-10-20",
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
                f"/exhibitions/{created_exhibition.id}",
                json={
                    "start_date": "2026-10-25",
                },
                headers=auth_headers,
            )

        assert response.status_code == 422

    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_exhibitions_requires_authentication(
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
                "/exhibitions",
            )

    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 401
