from app.core.security import verify_password
from app.models import AdminUser
from app.repositories.admin_user import get_admin_user_by_email
from sqlalchemy.ext.asyncio import AsyncSession


async def authenticate_admin(
    session: AsyncSession,
    email: str,
    password: str,
) -> AdminUser | None:
    admin = await get_admin_user_by_email(
        session,
        email,
    )

    if admin is None:
        return None

    if not admin.is_active:
        return None

    if not verify_password(
        password,
        admin.password_hash,
    ):
        return None

    return admin
