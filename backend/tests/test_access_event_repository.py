import pytest
from app.repositories.access_event import (
    count_accesses_by_exhibition,
    count_accesses_by_work,
    create_access_event,
)
from app.repositories.exhibition import create_exhibition
from app.repositories.work import create_work
from app.schemas.exhibition import ExhibitionCreate
from app.schemas.work import WorkCreate


@pytest.mark.asyncio
async def test_create_access_event_persists_event(db_session):
    exhibition = await create_exhibition(
        db_session,
        ExhibitionCreate(
            title="Exposição Métricas",
            description="Exposição usada para teste de métricas.",
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

    access_event = await create_access_event(
        db_session,
        work.id,
    )

    assert access_event.id is not None
    assert access_event.work_id == work.id
    assert access_event.accessed_at is not None


@pytest.mark.asyncio
async def test_count_accesses_by_work(db_session):
    exhibition = await create_exhibition(
        db_session,
        ExhibitionCreate(
            title="Exposição Métricas",
            description="Exposição usada para teste de métricas.",
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

    await create_access_event(db_session, work.id)
    await create_access_event(db_session, work.id)
    await create_access_event(db_session, work.id)

    total = await count_accesses_by_work(
        db_session,
        work.id,
    )

    assert total == 3


@pytest.mark.asyncio
async def test_count_accesses_by_exhibition(db_session):
    exhibition = await create_exhibition(
        db_session,
        ExhibitionCreate(
            title="Exposição Agregada",
            description="Exposição usada para teste agregado.",
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

    total = await count_accesses_by_exhibition(
        db_session,
        exhibition.id,
    )

    assert total == 3
