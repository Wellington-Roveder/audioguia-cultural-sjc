from uuid import UUID

from app.api.dependencies import get_current_admin
from app.database.session import get_session
from app.repositories.exhibition import (
    create_exhibition,
    delete_exhibition,
    get_exhibition_by_id,
    list_exhibitions,
    update_exhibition,
)
from app.schemas.exhibition import ExhibitionCreate, ExhibitionRead, ExhibitionUpdate
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/exhibitions",
    tags=["exhibitions"],
    dependencies=[Depends(get_current_admin)],
)


@router.post(
    "",
    response_model=ExhibitionRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_exhibition_endpoint(
    data: ExhibitionCreate,
    session: AsyncSession = Depends(get_session),
) -> ExhibitionRead:
    exhibition = await create_exhibition(session, data)
    return exhibition


@router.get(
    "",
    response_model=list[ExhibitionRead],
    status_code=status.HTTP_200_OK,
)
async def list_exhibitions_endpoint(
    session: AsyncSession = Depends(get_session),
) -> list[ExhibitionRead]:
    exhibitions = await list_exhibitions(session)
    return exhibitions


@router.get(
    "/{exhibition_id}",
    response_model=ExhibitionRead,
    status_code=status.HTTP_200_OK,
)
async def get_exhibition_endpoint(
    exhibition_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> ExhibitionRead:
    exhibition = await get_exhibition_by_id(
        session,
        exhibition_id,
    )

    if exhibition is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exhibition not found",
        )

    return exhibition


@router.patch(
    "/{exhibition_id}",
    response_model=ExhibitionRead,
    status_code=status.HTTP_200_OK,
)
async def update_exhibition_endpoint(
    exhibition_id: UUID,
    data: ExhibitionUpdate,
    session: AsyncSession = Depends(get_session),
) -> ExhibitionRead:
    exhibition = await get_exhibition_by_id(
        session,
        exhibition_id,
    )

    if exhibition is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exhibition not found",
        )

    new_start_date = (
        data.start_date
        if "start_date" in data.model_fields_set
        else exhibition.start_date
    )

    new_end_date = (
        data.end_date if "end_date" in data.model_fields_set else exhibition.end_date
    )

    if (
        new_start_date is not None
        and new_end_date is not None
        and new_start_date > new_end_date
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start_date must be before or equal to end_date",
        )

    return await update_exhibition(
        session,
        exhibition,
        data,
    )


@router.delete(
    "/{exhibition_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_exhibition_endpoint(
    exhibition_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> None:
    exhibition = await get_exhibition_by_id(
        session,
        exhibition_id,
    )

    if exhibition is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exhibition not found",
        )

    await delete_exhibition(
        session,
        exhibition,
    )
