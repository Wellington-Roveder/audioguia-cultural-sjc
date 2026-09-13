import uuid
from datetime import date, datetime, timezone
from typing import TYPE_CHECKING

from app.database.base import Base
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Index,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.work import Work


class Exhibition(Base):
    __tablename__ = "exhibitions"

    __table_args__ = (
        CheckConstraint(
            "length(trim(title)) > 0",
            name="ck_exhibitions_title_not_blank",
        ),
        CheckConstraint(
            "length(trim(description)) > 0",
            name="ck_exhibitions_description_not_blank",
        ),
        CheckConstraint(
            "end_date IS NULL or start_date IS NULL or end_date >= start_date",
            name="ck_exhibitions_valid_date_range",
        ),
        Index(
            "ix_exhibitions_is_active",
            "is_active",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    title: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    start_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    end_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
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

    works: Mapped[list["Work"]] = relationship(
        back_populates="exhibition",
    )
