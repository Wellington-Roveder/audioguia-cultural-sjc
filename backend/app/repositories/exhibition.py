from uuid import UUID

from app.models import Exhibition
from app.schemas.exhibition import ExhibitionCreate, ExhibitionUpdate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def create_exhibition(
    session: AsyncSession,
    data: ExhibitionCreate,
) -> Exhibition:
    exhibition = Exhibition(
        title=data.title,
        description=data.description,
        start_date=data.start_date,
        end_date=data.end_date,
    )

    session.add(exhibition)
    await session.commit()
    await session.refresh(exhibition)

    return exhibition


async def get_exhibition_by_id(
    session: AsyncSession,
    exhibition_id: UUID,
) -> Exhibition | None:
    result = await session.execute(
        select(Exhibition).where(Exhibition.id == exhibition_id)
    )

    return result.scalar_one_or_none()


async def list_exhibitions(
    session: AsyncSession,
) -> list[Exhibition]:
    result = await session.execute(
        select(Exhibition).order_by(Exhibition.created_at.desc())
    )

    return list(result.scalars().all())


async def update_exhibition(
    session: AsyncSession,
    exhibition: Exhibition,
    data: ExhibitionUpdate,
) -> Exhibition:
    update_data = data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(exhibition, field, value)

    await session.commit()
    await session.refresh(exhibition)

    return exhibition


async def delete_exhibition(
    session: AsyncSession,
    exhibition: Exhibition,
) -> None:
    await session.delete(exhibition)
    await session.commit()
