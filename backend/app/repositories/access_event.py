from app.models import AccessEvent
from sqlalchemy.ext.asyncio import AsyncSession


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
