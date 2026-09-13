import pytest

from app.repositories.admin_user import (
    create_admin_user,
    get_admin_user_by_email,
)


@pytest.mark.asyncio
async def test_create_admin_user(db_session):
    admin = await create_admin_user(
        db_session,
        email="admin@audioguia.local",
        password_hash="fake-hash",
    )

    assert admin.id is not None
    assert admin.email == "admin@audioguia.local"
    assert admin.password_hash == "fake-hash"
    assert admin.is_active is True


@pytest.mark.asyncio
async def test_get_admin_user_by_email(db_session):
    await create_admin_user(
        db_session,
        email="curadoria@audioguia.local",
        password_hash="fake-hash",
    )

    admin = await get_admin_user_by_email(
        db_session,
        "curadoria@audioguia.local",
    )

    assert admin is not None
    assert admin.email == "curadoria@audioguia.local"


@pytest.mark.asyncio
async def test_get_admin_user_by_email_returns_none(db_session):
    admin = await get_admin_user_by_email(
        db_session,
        "naoexiste@audioguia.local",
    )

    assert admin is None
