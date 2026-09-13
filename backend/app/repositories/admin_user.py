from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AdminUser


async def create_admin_user(
    session: AsyncSession,
    email: str,
    password_hash: str,
) -> AdminUser:
    admin_user = AdminUser(
        email=email,
        password_hash=password_hash,
    )

    session.add(admin_user)
    await session.commit()
    await session.refresh(admin_user)

    return admin_user


async def get_admin_user_by_email(
    session: AsyncSession,
    email: str,
) -> AdminUser | None:
    result = await session.execute(select(AdminUser).where(AdminUser.email == email))

    return result.scalar_one_or_none()
