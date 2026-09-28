from app.core.config import settings


def test_async_database_url_converts_heroku_postgres_url(monkeypatch):
    monkeypatch.setattr(
        settings,
        "database_url",
        "postgres://user:password@host:5432/database",
    )

    assert settings.async_database_url == (
        "postgresql+asyncpg://user:password@host:5432/database"
    )


def test_async_database_url_converts_standard_postgresql_url(monkeypatch):
    monkeypatch.setattr(
        settings,
        "database_url",
        "postgresql://user:password@host:5432/database",
    )

    assert settings.async_database_url == (
        "postgresql+asyncpg://user:password@host:5432/database"
    )


def test_async_database_url_keeps_asyncpg_url(monkeypatch):
    url = "postgresql+asyncpg://user:password@host:5432/database"

    monkeypatch.setattr(settings, "database_url", url)

    assert settings.async_database_url == url
