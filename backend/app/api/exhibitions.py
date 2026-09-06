from uuid import UUID

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

    updated_exhibition = await update_exhibition(
        session,
        exhibition,
        data,
    )

    return updated_exhibition


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
