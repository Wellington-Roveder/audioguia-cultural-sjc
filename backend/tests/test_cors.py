from app.core.config import settings
from app.main import app


def test_cors_uses_configured_origins():
    middleware = next(
        middleware
        for middleware in app.user_middleware
        if middleware.cls.__name__ == "CORSMiddleware"
    )

    configured_origins = [
        origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()
    ]

    assert middleware.kwargs["allow_origins"] == configured_origins
    assert middleware.kwargs["allow_credentials"] is True
