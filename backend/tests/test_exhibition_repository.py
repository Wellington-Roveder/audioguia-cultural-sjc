from datetime import date
from uuid import uuid4

import pytest
from app.models import Exhibition
from app.repositories.exhibition import (
    create_exhibition,
    delete_exhibition,
    get_exhibition_by_id,
    list_exhibitions,
    update_exhibition,
)
from app.schemas.exhibition import ExhibitionCreate, ExhibitionUpdate
from sqlalchemy import select


@pytest.mark.asyncio
async def test_create_exhibition_persists_exhibition(db_session):
    data = ExhibitionCreate(
        title="Exposição de Integração",
        description="Criada pelo teste de integração.",
    )

    exhibition = await create_exhibition(
        db_session,
        data,
    )

    assert exhibition.id is not None
    assert exhibition.title == data.title
    assert exhibition.description == data.description
    assert exhibition.is_active is True

    result = await db_session.execute(
        select(Exhibition).where(Exhibition.id == exhibition.id)
    )

    stored_exhibition = result.scalar_one()

    assert stored_exhibition.id == exhibition.id
    assert stored_exhibition.title == data.title
    assert stored_exhibition.description == data.description


@pytest.mark.asyncio
async def test_get_exhibition_by_id_returns_exhibition(db_session):
    data = ExhibitionCreate(
        title="Exposição para Busca",
        description="Exposição criada para testar busca por ID.",
    )

    created_exhibition = await create_exhibition(
        db_session,
        data,
    )

    found_exhibition = await get_exhibition_by_id(
        db_session,
        created_exhibition.id,
    )

    assert found_exhibition is not None
    assert found_exhibition.id == created_exhibition.id
    assert found_exhibition.title == data.title
    assert found_exhibition.description == data.description


@pytest.mark.asyncio
async def test_get_exhibition_by_id_returns_none_when_not_found(db_session):
    exhibition_id = uuid4()

    found_exhibition = await get_exhibition_by_id(
        db_session,
        exhibition_id,
    )

    assert found_exhibition is None


@pytest.mark.asyncio
async def test_list_exhibitions_returns_created_exhibitions(db_session):
    first_data = ExhibitionCreate(
        title="Primeira Exposição",
        description="Primeira exposição do teste.",
    )

    second_data = ExhibitionCreate(
        title="Segunda Exposição",
        description="Segunda exposiçao do teste.",
    )

    first_exhibition = await create_exhibition(
        db_session,
        first_data,
    )

    second_exhibition = await create_exhibition(
        db_session,
        second_data,
    )

    exhibitions = await list_exhibitions(db_session)

    exhibition_ids = [exhibition.id for exhibition in exhibitions]

    assert first_exhibition.id in exhibition_ids
    assert second_exhibition.id in exhibition_ids


@pytest.mark.asyncio
async def test_list_exhibitions_returns_empty_list_when_no_exhibitions(db_session):
    exhibitions = await list_exhibitions(db_session)

    assert exhibitions == []


@pytest.mark.asyncio
async def test_update_exhibition_updates_selected_fields(db_session):
    created_exhibition = await create_exhibition(
        db_session,
        ExhibitionCreate(
            title="Título Antigo",
            description="Descrição antiga.",
        ),
    )

    updated_exhibition = await update_exhibition(
        db_session,
        created_exhibition,
        ExhibitionUpdate(
            title="Título Atualizado",
        ),
    )

    assert updated_exhibition.id == created_exhibition.id
    assert updated_exhibition.title == "Título Atualizado"
    assert updated_exhibition.description == "Descrição antiga."


@pytest.mark.asyncio
async def test_update_exhibition_can_clear_optional_date(db_session):
    created_exhibition = await create_exhibition(
        db_session,
        ExhibitionCreate(
            title="Exposição",
            description="Descrição.",
            start_date=date(2026, 9, 10),
        ),
    )

    updated_exhibition = await update_exhibition(
        db_session,
        created_exhibition,
        ExhibitionUpdate(start_date=None),
    )

    assert updated_exhibition.start_date is None


@pytest.mark.asyncio
async def test_delete_exhibition_removes_exhibition(db_session):
    created_exhibition = await create_exhibition(
        db_session,
        ExhibitionCreate(
            title="Exposição para Exclusão",
            description="Será removida.",
        ),
    )

    exhibition_id = created_exhibition.id

    await delete_exhibition(
        db_session,
        created_exhibition,
    )

    found_exhibition = await get_exhibition_by_id(
        db_session,
        exhibition_id,
    )

    assert found_exhibition is None


@pytest.mark.asyncio
async def test_delete_exhibition_does_not_affect_other_exhibitions(db_session):
    first_exhibition = await create_exhibition(
        db_session,
        ExhibitionCreate(
            title="Primeira Exposição",
            description="Será removida.",
        ),
    )

    second_exhibition = await create_exhibition(
        db_session,
        ExhibitionCreate(
            title="Segunda Exposição",
            description="Deve permanecer.",
        ),
    )

    await delete_exhibition(
        db_session,
        first_exhibition,
    )

    remaining_exhibition = await get_exhibition_by_id(
        db_session,
        second_exhibition.id,
    )

    assert remaining_exhibition is not None
    assert remaining_exhibition.id == second_exhibition.id
