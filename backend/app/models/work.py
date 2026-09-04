import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from app.database.base import Base
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.access_event import AccessEvent
    from app.models.exhibition import Exhibition


class Work(Base):
    __tablename__ = "works"
    __table_args__ = (
        CheckConstraint(
            "length(trim(title)) > 0",
            name="ck_works_title_not_blank",
        ),
        CheckConstraint(
            "length(trim(description)) > 0",
            name="ck_works_description_not_blank",
        ),
        CheckConstraint(
            "length(trim(public_slug)) > 0",
            name="ck_works_public_slug_not_blank",
        ),
        Index("ix_works_exhibition_id", "exhibition_id"),
        Index(
            "ix_works_is_active",
            "is_active",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    exhibition_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "exhibitions.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    artist: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    audio_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    audio_description_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    libras_video_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    public_slug: Mapped[str | None] = mapped_column(
        String(180),
        nullable=False,
        unique=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    exhibition: Mapped[list["Exhibition"]] = relationship(
        back_populates="works",
    )

    access_events: Mapped[list["AccessEvent"]] = relationship(
        back_populates="work",
    )
