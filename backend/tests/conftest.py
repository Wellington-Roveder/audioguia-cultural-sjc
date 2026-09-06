import pytest_asyncio
from app.core.config import settings
from app.models import AccessEvent, Exhibition, Work
from sqlalchemy import delete
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

dev_database = make_url(settings.database_url).database
test_database = make_url(settings.test_database_url).database

if dev_database == test_database:
    raise RuntimeError(
        "TEST_DATABASE_URL must point to a different database than DATABASE_URL"
    )


test_engine = create_async_engine(
    settings.test_database_url,
    poolclass=NullPool,
)

TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest_asyncio.fixture
async def db_session():
    async with TestSessionLocal() as session:
        yield session

        await session.rollback()

        await session.execute(delete(AccessEvent))
        await session.execute(delete(Work))
        await session.execute(delete(Exhibition))
        await session.commit()
