from uuid import UUID, uuid4

from app.models import Work
from app.schemas.work import WorkCreate, WorkUpdate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


def generate_public_slug() -> str:
    return uuid4().hex


async def create_work(
    session: AsyncSession,
    data: WorkCreate,
) -> Work:
    work = Work(
        exhibition_id=data.exhibition_id,
        title=data.title,
        artist=data.artist,
        description=data.description,
        audio_url=data.audio_url,
        audio_description_url=data.audio_description_url,
        libras_video_url=data.libras_video_url,
        public_slug=generate_public_slug(),
    )

    session.add(work)
    await session.commit()
    await session.refresh(work)

    return work


async def get_work_by_id(
    session: AsyncSession,
    work_id: UUID,
) -> Work | None:
    result = await session.execute(select(Work).where(Work.id == work_id))

    return result.scalar_one_or_none()


async def list_works_by_exhibition(
    session: AsyncSession,
    exhibition_id: UUID,
) -> list[Work]:
    result = await session.execute(
        select(Work)
        .where(Work.exhibition_id == exhibition_id)
        .order_by(Work.created_at.desc())
    )

    return list(result.scalars().all())


async def update_work(
    session: AsyncSession,
    work: Work,
    data: WorkUpdate,
) -> Work:
    update_data = data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(work, field, value)

    await session.commit()
    await session.refresh(work)

    return work


async def delete_work(
    session: AsyncSession,
    work: Work,
) -> None:
    await session.delete(work)
    await session.commit()
