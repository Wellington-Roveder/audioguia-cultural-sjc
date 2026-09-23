from io import BytesIO
from uuid import UUID

from app.api.dependencies import get_current_admin
from app.core.storage import get_storage_service
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
from app.services.storage import StorageService
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

router = APIRouter(
    prefix="/works",
    tags=["works"],
    dependencies=[Depends(get_current_admin)],
)


MAX_AUDIO_SIZE = 10 * 1024 * 1024
MAX_VIDEO_SIZE = 50 * 1024 * 1024


async def validate_mp3_file(file: UploadFile) -> None:
    if file.content_type != "audio/mpeg":
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only MP3 audio files are allowed",
        )

    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > MAX_AUDIO_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Audio file exceeds the 10 MB limit",
        )

    header = await file.read(3)

    is_id3 = header == b"ID3"
    is_mpeg_frame = (
        len(header) >= 2 and header[0] == 0xFF and (header[1] & 0xE0) == 0xE0
    )

    await file.seek(0)

    if not (is_id3 or is_mpeg_frame):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Invalid MP3 file",
        )


async def validate_mp4_file(file: UploadFile) -> None:
    if file.content_type != "video/mp4":
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only MP4 video files are allowed",
        )

    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > MAX_VIDEO_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Video file exceeds the 50 MB limit",
        )

    header = await file.read(12)

    await file.seek(0)

    if len(header) < 8 or header[4:8] != b"ftyp":
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Invalid MP4 file",
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


@router.post(
    "/{work_id}/media/audio",
    response_model=WorkRead,
    status_code=status.HTTP_201_CREATED,
)
async def upload_work_audio(
    work_id: UUID,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
    storage: StorageService = Depends(get_storage_service),
) -> WorkRead:
    work = await get_work_by_id(session, work_id)

    if work is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Work not found",
        )

    await validate_mp3_file(file)

    object_key = f"works/{work.id}/audio/{work.id}.mp3"

    await run_in_threadpool(
        storage.upload,
        file_object=file.file,
        object_key=object_key,
        content_type=file.content_type,
    )

    return await update_work(
        session,
        work,
        WorkUpdate(audio_url=object_key),
    )


@router.post(
    "/{work_id}/media/audio-description",
    response_model=WorkRead,
    status_code=status.HTTP_201_CREATED,
)
async def upload_work_audio_description(
    work_id: UUID,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
    storage: StorageService = Depends(get_storage_service),
) -> WorkRead:
    work = await get_work_by_id(session, work_id)

    if work is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Work not found",
        )

    await validate_mp3_file(file)

    object_key = f"works/{work.id}/audio-description/{work.id}.mp3"

    await run_in_threadpool(
        storage.upload,
        file_object=file.file,
        object_key=object_key,
        content_type=file.content_type,
    )

    return await update_work(
        session,
        work,
        WorkUpdate(
            audio_description_url=object_key,
        ),
    )


@router.post(
    "/{work_id}/media/libras",
    response_model=WorkRead,
    status_code=status.HTTP_201_CREATED,
)
async def upload_work_libras_video(
    work_id: UUID,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
    storage: StorageService = Depends(get_storage_service),
) -> WorkRead:
    work = await get_work_by_id(session, work_id)

    if work is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Work not found",
        )

    await validate_mp4_file(file)

    object_key = f"works/{work.id}/libras/{work.id}.mp4"

    await run_in_threadpool(
        storage.upload,
        file_object=file.file,
        object_key=object_key,
        content_type=file.content_type,
    )

    return await update_work(
        session,
        work,
        WorkUpdate(
            libras_video_url=object_key,
        ),
    )


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
