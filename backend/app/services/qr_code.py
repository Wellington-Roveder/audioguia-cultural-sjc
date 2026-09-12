from io import BytesIO

import qrcode
from app.core.config import settings


def build_public_work_url(public_slug: str) -> str:
    base_url = settings.public_frontend_url.rstrip("/")
    return f"{base_url}/obra/{public_slug}"


def generate_qr_png(public_slug: str) -> bytes:
    public_url = build_public_work_url(public_slug)

    qr = qrcode.QRCode(
        version=None,
        box_size=10,
        border=4,
    )
    qr.add_data(public_url)
    qr.make(fit=True)

    image = qr.make_image()

    buffer = BytesIO()
    image.save(buffer, format="PNG")

    return buffer.getvalue()
