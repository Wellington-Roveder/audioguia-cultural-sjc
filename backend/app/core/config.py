from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    app_env: str = "development"

    database_url: str
    test_database_url: str | None = None

    secret_key: str
    algorithm: str
    access_token_expires_minutes: int = 60

    public_frontend_url: str

    storage_endpoint_url: str
    storage_access_key_id: str
    storage_secret_access_key: str
    storage_bucket_name: str

    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def async_database_url(self) -> str:
        url = self.database_url

        if url.startswith("postgres://"):
            return url.replace(
                "postgres://",
                "postgresql+asyncpg://",
                1,
            )

        if url.startswith("postgresql://"):
            return url.replace(
                "postgresql://",
                "postgresql+asyncpg://",
                1,
            )

        return url


settings = Settings()
