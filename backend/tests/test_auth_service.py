import pytest
from app.core.security import hash_password
from app.repositories.admin_user import create_admin_user
from app.services.auth import authenticate_admin


@pytest.mark.asyncio
async def test_authenticate_admin_with_valid_credentials(db_session):
    password = "senha-segura-123"

    admin = await create_admin_user(
        db_session,
        email="admin@audioguia.local",
        password_hash=hash_password(password),
    )

    authenticated = await authenticate_admin(
        db_session,
        email="admin@audioguia.local",
        password=password,
    )

    assert authenticated is not None
    assert authenticated.id == admin.id
    assert authenticated.email == admin.email


@pytest.mark.asyncio
async def test_authenticate_admin_with_wrong_password(db_session):
    admin = await create_admin_user(
        db_session,
        email="admin@audioguia.local",
        password_hash=hash_password("senha-correta"),
    )

    authenticated = await authenticate_admin(
        db_session,
        email=admin.email,
        password="senha-errada",
    )

    assert authenticated is None


@pytest.mark.asyncio
async def test_authenticate_admin_with_unknown_email(db_session):
    authenticated = await authenticate_admin(
        db_session,
        email="naoexiste@audioguia.local",
        password="qualquer-senha",
    )

    assert authenticated is None


@pytest.mark.asyncio
async def test_authenticate_admin_with_inactive_user(db_session):
    admin = await create_admin_user(
        db_session,
        email="inativo@audioguia.local",
        password_hash=hash_password("senha-segura"),
    )

    admin.is_active = False
    await db_session.commit()

    authenticated = await authenticate_admin(
        db_session,
        email=admin.email,
        password="senha-segura",
    )

    assert authenticated is None
