from uuid import UUID

from app.database.session import get_session
from app.repositories.access_event import (
    count_accesses_by_exhibition,
    count_accesses_by_work,
)
from app.repositories.exhibition import get_exhibition_by_id
from app.repositories.work import get_work_by_id
from app.schemas.metrics import (
    ExhibitionMetricsRead,
    WorkMetricsRead,
)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/metrics",
    tags=["metrics"],
)


@router.get(
    "/works/{work_id}",
    response_model=WorkMetricsRead,
    status_code=status.HTTP_200_OK,
)
async def get_work_metrics(
    work_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    work = await get_work_by_id(
        session,
        work_id,
    )

    if work is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Work not found",
        )

    access_count = await count_accesses_by_work(
        session,
        work_id,
    )

    return WorkMetricsRead(
        work_id=work_id,
        access_count=access_count,
    )


@router.get(
    "/exhibitions/{exhibition_id}",
    response_model=ExhibitionMetricsRead,
    status_code=status.HTTP_200_OK,
)
async def get_exhibition_metrics(
    exhibition_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    exhibition = await get_exhibition_by_id(
        session,
        exhibition_id,
    )

    if exhibition is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exhibition not found",
        )

    access_count = await count_accesses_by_exhibition(
        session,
        exhibition_id,
    )

    return ExhibitionMetricsRead(
        exhibition_id=exhibition_id,
        access_count=access_count,
    )
