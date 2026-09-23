from app.core.storage import get_storage_service
from app.database.session import get_session
from app.repositories.access_event import create_access_event
from app.repositories.work import get_work_by_public_slug
from app.schemas.public_work import PublicWorkRead
from app.services.storage import StorageService
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

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


@router.get(
    "/{public_slug}/media/audio",
    status_code=status.HTTP_200_OK,
)
async def get_public_work_audio(
    public_slug: str,
    session: AsyncSession = Depends(get_session),
    storage: StorageService = Depends(get_storage_service),
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

    if not work.audio_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audio not found",
        )

    audio_file = await run_in_threadpool(
        storage.download,
        object_key=work.audio_url,
    )

    return StreamingResponse(
        audio_file,
        media_type="audio/mpeg",
    )


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


@router.get(
    "/{public_slug}/media/audio-description",
    status_code=status.HTTP_200_OK,
)
async def get_public_work_audio_description(
    public_slug: str,
    session: AsyncSession = Depends(get_session),
    storage: StorageService = Depends(get_storage_service),
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

    if not work.audio_description_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audio description not found",
        )

    audio_file = await run_in_threadpool(
        storage.download,
        object_key=work.audio_description_url,
    )

    return StreamingResponse(
        audio_file,
        media_type="audio/mpeg",
    )


@router.get(
    "/{public_slug}/media/libras",
    status_code=status.HTTP_200_OK,
)
async def get_public_work_libras_video(
    public_slug: str,
    session: AsyncSession = Depends(get_session),
    storage: StorageService = Depends(get_storage_service),
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

    if not work.libras_video_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Libras video not found",
        )

    video_file = await run_in_threadpool(
        storage.download,
        object_key=work.libras_video_url,
    )

    return StreamingResponse(
        video_file,
        media_type="video/mp4",
    )
