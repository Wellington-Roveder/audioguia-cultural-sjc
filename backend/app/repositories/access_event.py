from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AccessEvent, Work


async def create_access_event(
    session: AsyncSession,
    work_id,
) -> AccessEvent:
    access_event = AccessEvent(
        work_id=work_id,
    )

    session.add(access_event)
    await session.commit()
    await session.refresh(access_event)

    return access_event


async def count_accesses_by_work(
    session: AsyncSession,
    work_id: UUID,
) -> int:
    result = await session.execute(
        select(func.count(AccessEvent.id)).where(
            AccessEvent.work_id == work_id
        )
    )

    return result.scalar_one()


async def count_accesses_by_exhibition(
    session: AsyncSession,
    exhibition_id: UUID,
) -> int:
    result = await session.execute(
        select(func.count(AccessEvent.id))
        .join(
            Work,
            AccessEvent.work_id == Work.id,
        )
        .where(
            Work.exhibition_id == exhibition_id
        )
    )

    return result.scalar_one()