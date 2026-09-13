from io import BytesIO
from uuid import UUID

from app.database.session import get_session
from app.repositories.exhibition import get_exhibition_by_id
from app.repositories.work import (
    create_work,
    delete_work,
    get_work_by_id,
    list_works_by_exhibition,
    update_work,
)
from app.schemas.work import WorkCreate, WorkRead, WorkUpdate
from app.services.qr_code import generate_qr_png
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/works",
    tags=["works"],
)


@router.post(
    "",
    response_model=WorkRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_work_endpoint(
    data: WorkCreate,
    session: AsyncSession = Depends(get_session),
) -> WorkRead:
    exhibition = await get_exhibition_by_id(
        session,
        data.exhibition_id,
    )

    if exhibition is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exhibition not found",
        )

    work = await create_work(
        session,
        data,
    )

    return work


@router.get(
    "/{work_id}",
    response_model=WorkRead,
    status_code=status.HTTP_200_OK,
)
async def get_work_endpoint(
    work_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> WorkRead:
    work = await get_work_by_id(
        session,
        work_id,
    )

    if work is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Work not found",
        )

    return work


@router.get(
    "/by-exhibition/{exhibition_id}",
    response_model=list[WorkRead],
    status_code=status.HTTP_200_OK,
)
async def list_works_by_exhibition_endpoint(
    exhibition_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> list[WorkRead]:
    exhibition = await get_exhibition_by_id(
        session,
        exhibition_id,
    )

    if exhibition is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exhibition not found",
        )

    works = await list_works_by_exhibition(
        session,
        exhibition_id,
    )

    return works


@router.patch(
    "/{work_id}",
    response_model=WorkRead,
    status_code=status.HTTP_200_OK,
)
async def update_work_endpoint(
    work_id: UUID,
    data: WorkUpdate,
    session: AsyncSession = Depends(get_session),
) -> WorkRead:
    work = await get_work_by_id(
        session,
        work_id,
    )

    if work is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Work not found",
        )

    return await update_work(
        session,
        work,
        data,
    )


@router.delete(
    "/{work_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_work_endpoint(
    work_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> None:
    work = await get_work_by_id(
        session,
        work_id,
    )

    if work is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Work not found",
        )

    await delete_work(
        session,
        work,
    )


@router.get("/{work_id}/qr")
async def get_work_qr(
    work_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    work = await get_work_by_id(session, work_id)

    if work is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Work not found",
        )

    qr_bytes = generate_qr_png(work.public_slug)

    return StreamingResponse(
        BytesIO(qr_bytes),
        media_type="image/png",
        headers={
            "Content-Disposition": (f'attachment; filename="qr-{work.public_slug}.png"')
        },
    )
