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
