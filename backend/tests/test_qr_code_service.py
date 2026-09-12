from app.services.qr_code import build_public_work_url, generate_qr_png


def test_build_public_work_url():
    public_slug = "abc123"

    result = build_public_work_url(public_slug)

    assert result == "http://localhost:3000/obra/abc123"


def test_build_public_work_url_removes_trailing_slash(monkeypatch):
    monkeypatch.setattr(
        "app.services.qr_code.settings.public_frontend_url",
        "https://dominio.com/",
    )

    result = build_public_work_url("abc123")

    assert result == "https://dominio.com/obra/abc123"


def test_generate_qr_png_returns_png_bytes():
    result = generate_qr_png("abc123")

    assert isinstance(result, bytes)
    assert result.startswith(b"\x89PNG\r\n\x1a\n")
