from app.core.security import create_access_token
from app.database.session import get_session
from app.schemas.auth import AdminLogin, TokenResponse
from app.services.auth import authenticate_admin
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_current_admin
from app.models import AdminUser

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
async def login(
    credentials: AdminLogin,
    session: AsyncSession = Depends(get_session),
):
    admin = await authenticate_admin(
        session,
        email=str(credentials.email),
        password=credentials.password,
    )

    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    access_token = create_access_token(subject=str(admin.id))

    return TokenResponse(
        access_token=access_token,
    )

@router.get("/me")
async def get_me(
    admin: AdminUser = Depends(get_current_admin),
):
    return {
        "id": str(admin.id),
        "email": admin.email,
    }