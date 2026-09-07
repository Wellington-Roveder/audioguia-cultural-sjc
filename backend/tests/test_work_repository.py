from uuid import uuid4

import pytest
from app.repositories.exhibition import create_exhibition
from app.repositories.work import (
    create_work,
    delete_work,
    get_work_by_id,
    list_works_by_exhibition,
    update_work,
)
from app.schemas.exhibition import ExhibitionCreate
from app.schemas.work import WorkCreate, WorkUpdate


@pytest.mark.asyncio
async def test_create_work_persists_work(db_session):
    exhibition = await create_exhibition(
        db_session,
        ExhibitionCreate(
            title="Exposição Teste",
            description="Exposição usada no teste de obra.",
        ),
    )

    work = await create_work(
        db_session,
        WorkCreate(
            exhibition_id=exhibition.id,
            title="Memórias do Vale",
            artist="Artista Teste",
            description="Descrição da obra.",
        ),
    )

    assert work.id is not None
    assert work.exhibition_id == exhibition.id
    assert work.title == "Memórias do Vale"
    assert work.artist == "Artista Teste"
    assert work.description == "Descrição da obra."
    assert work.public_slug
    assert work.is_active is True


@pytest.mark.asyncio
async def test_get_work_by_id_returns_work(db_session):
    exhibition = await create_exhibition(
        db_session,
        ExhibitionCreate(
            title="Exposição de Teste",
            description="Exposição para teste de busca.",
        ),
    )

    created_work = await create_work(
        db_session,
        WorkCreate(
            exhibition_id=exhibition.id,
            title="Obra para Busca",
            description="Descroção da obra.",
        ),
    )

    found_work = await get_work_by_id(
        db_session,
        created_work.id,
    )

    assert found_work is not None
    assert found_work.id == created_work.id
    assert found_work.title == "Obra para Busca"


@pytest.mark.asyncio
async def test_get_work_by_id_returns_none_when_not_found(db_session):
    found_work = await get_work_by_id(
        db_session,
        uuid4(),
    )

    assert found_work is None


@pytest.mark.asyncio
async def test_list_works_by_exhibition_returns_only_related_works(db_session):
    exhibition_a = await create_exhibition(
        db_session,
        ExhibitionCreate(
            title="Exposição A",
            description="Descrição A.",
        ),
    )

    exhibition_b = await create_exhibition(
        db_session,
        ExhibitionCreate(
            title="Exposição B",
            description="Descrição B.",
        ),
    )

    await create_work(
        db_session,
        WorkCreate(
            exhibition_id=exhibition_a.id,
            title="Obra A1",
            description="Descrição A1.",
        ),
    )

    await create_work(
        db_session,
        WorkCreate(
            exhibition_id=exhibition_a.id,
            title="Obra A2",
            description="Descrição A2.",
        ),
    )

    await create_work(
        db_session,
        WorkCreate(
            exhibition_id=exhibition_b.id,
            title="Obra B1",
            description="Descrição B1.",
        ),
    )

    works = await list_works_by_exhibition(
        db_session,
        exhibition_a.id,
    )

    assert len(works) == 2
    assert {work.title for work in works} == {
        "Obra A1",
        "Obra A2",
    }


@pytest.mark.asyncio
async def test_list_works_by_exhibition_returns_empty_list(db_session):
    exhibition = await create_exhibition(
        db_session,
        ExhibitionCreate(
            title="Exposição sem Obras",
            description="Descrição.",
        ),
    )

    works = await list_works_by_exhibition(
        db_session,
        exhibition.id,
    )

    assert works == []


@pytest.mark.asyncio
async def test_update_work_updates_selected_fields(db_session):
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

    updated_work = await update_work(
        db_session,
        work,
        WorkUpdate(
            title="Título Novo",
        ),
    )

    assert updated_work.title == "Título Novo"
    assert updated_work.artist == "Artista Antigo"
    assert updated_work.description == "Descrição antiga."


@pytest.mark.asyncio
async def test_update_work_can_clear_optional_field(db_session):
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
            title="Obra Teste",
            artist="Artista Teste",
            description="Descrição.",
        ),
    )

    updated_work = await update_work(
        db_session,
        work,
        WorkUpdate(
            artist=None,
        ),
    )

    assert updated_work.artist is None


@pytest.mark.asyncio
async def test_delete_work_removes_work(db_session):
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

    await delete_work(
        db_session,
        work,
    )

    found_work = await get_work_by_id(
        db_session,
        work_id,
    )

    assert found_work is None


@pytest.mark.asyncio
async def test_delete_work_does_not_remove_other_works(db_session):
    exhibition = await create_exhibition(
        db_session,
        ExhibitionCreate(
            title="Exposição Teste",
            description="Descrição.",
        ),
    )

    work_a = await create_work(
        db_session,
        WorkCreate(
            exhibition_id=exhibition.id,
            title="Obra A",
            description="Descrição A.",
        ),
    )

    work_b = await create_work(
        db_session,
        WorkCreate(
            exhibition_id=exhibition.id,
            title="Obra B",
            description="Descrição B.",
        ),
    )

    await delete_work(
        db_session,
        work_a,
    )

    found_work_b = await get_work_by_id(
        db_session,
        work_b.id,
    )

    assert found_work_b is not None
    assert found_work_b.id == work_b.id


@pytest.mark.asyncio
async def test_create_work_generates_unique_public_slugs(db_session):
    exhibition = await create_exhibition(
        db_session,
        ExhibitionCreate(
            title="Exposição Teste",
            description="Descrição.",
        ),
    )

    work_a = await create_work(
        db_session,
        WorkCreate(
            exhibition_id=exhibition.id,
            title="Obra A",
            description="Descrição A.",
        ),
    )

    work_b = await create_work(
        db_session,
        WorkCreate(
            exhibition_id=exhibition.id,
            title="Obra B",
            description="Descrição B.",
        ),
    )

    assert work_a.public_slug
    assert work_b.public_slug
    assert work_a.public_slug != work_b.public_slug
