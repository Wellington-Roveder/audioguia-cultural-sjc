import pytest
from app.core.security import hash_password
from app.database.session import get_session
from app.main import app
from app.repositories.admin_user import create_admin_user
from httpx import ASGITransport, AsyncClient


@pytest.mark.asyncio
async def test_login_with_valid_credentials(db_session):
    password = "senha-segura-123"

    admin = await create_admin_user(
        db_session,
        email="admin@example.com",
        password_hash=hash_password(password),
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
                "/auth/login",
                json={
                    "email": admin.email,
                    "password": password,
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["access_token"]
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_with_wrong_password(db_session):
    admin = await create_admin_user(
        db_session,
        email="admin@example.com",
        password_hash=hash_password("senha-correta"),
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
                "/auth/login",
                json={
                    "email": admin.email,
                    "password": "senha-errada",
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Invalid credentials",
    }


@pytest.mark.asyncio
async def test_login_with_unknown_email(db_session):
    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.post(
                "/auth/login",
                json={
                    "email": "naoexiste@example.com",
                    "password": "qualquer-senha",
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Invalid credentials",
    }


@pytest.mark.asyncio
async def test_login_with_inactive_admin(db_session):
    password = "senha-segura-123"

    admin = await create_admin_user(
        db_session,
        email="inativo@example.com",
        password_hash=hash_password(password),
    )

    admin.is_active = False
    await db_session.commit()

    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.post(
                "/auth/login",
                json={
                    "email": admin.email,
                    "password": password,
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Invalid credentials",
    }
