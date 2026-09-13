from uuid import uuid4

import pytest
from app.api.dependencies import get_current_admin
from app.core.security import create_access_token, hash_password
from app.database.session import get_session
from app.main import app
from app.models import AdminUser
from app.repositories.admin_user import create_admin_user
from fastapi import Depends
from httpx import ASGITransport, AsyncClient


@app.get("/test/current-admin")
async def current_admin_test(
    admin: AdminUser = Depends(get_current_admin),
):
    return {
        "id": str(admin.id),
        "email": admin.email,
    }


@pytest.mark.asyncio
async def test_get_current_admin_with_valid_token(db_session):
    admin = await create_admin_user(
        db_session,
        email="admin@example.com",
        password_hash=hash_password("senha-segura"),
    )

    token = create_access_token(str(admin.id))

    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.get(
                "/test/current-admin",
                headers={
                    "Authorization": f"Bearer {token}",
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "id": str(admin.id),
        "email": admin.email,
    }


@pytest.mark.asyncio
async def test_get_current_admin_with_invalid_token(db_session):
    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.get(
                "/test/current-admin",
                headers={
                    "Authorization": "Bearer invalid-token",
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_admin_with_invalid_subject(db_session):
    token = create_access_token("not-a-uuid")

    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.get(
                "/test/current-admin",
                headers={
                    "Authorization": f"Bearer {token}",
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_admin_with_unknown_admin(db_session):
    token = create_access_token(str(uuid4()))

    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.get(
                "/test/current-admin",
                headers={
                    "Authorization": f"Bearer {token}",
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_admin_with_inactive_admin(db_session):
    admin = await create_admin_user(
        db_session,
        email="inativo@example.com",
        password_hash=hash_password("senha-segura"),
    )

    admin.is_active = False
    await db_session.commit()

    token = create_access_token(str(admin.id))

    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.get(
                "/test/current-admin",
                headers={
                    "Authorization": f"Bearer {token}",
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 401
