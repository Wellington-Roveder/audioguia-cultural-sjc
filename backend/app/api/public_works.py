from app.database.session import get_session
from app.repositories.access_event import create_access_event
from app.repositories.work import get_work_by_public_slug
from app.schemas.public_work import PublicWorkRead
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/public/works",
    tags=["public works"],
)


@router.get(
    "/{public_slug}",
    response_model=PublicWorkRead,
    status_code=status.HTTP_200_OK,
)
async def get_public_work_endpoint(
    public_slug: str,
    session: AsyncSession = Depends(get_session),
) -> PublicWorkRead:
    work = await get_work_by_public_slug(
        session,
        public_slug,
    )

    if work is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Work not found",
        )

    return work


@router.post(
    "/{public_slug}/access",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def register_public_work_access(
    public_slug: str,
    session: AsyncSession = Depends(get_session),
):
    work = await get_work_by_public_slug(
        session,
        public_slug,
    )

    if work is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Work not found",
        )

    await create_access_event(
        session,
        work.id,
    )
