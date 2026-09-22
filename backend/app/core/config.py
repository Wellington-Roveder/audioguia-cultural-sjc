from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str
    secret_key: str
    test_database_url: str
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    public_frontend_url: str
    algorithm: str
    access_token_expires_minutes: int = 60
    storage_endpoint_url: str
    storage_access_key_id: str
    storage_secret_access_key: str
    storage_bucket_name: str


settings = Settings()
