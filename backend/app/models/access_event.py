import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from app.database.base import Base
from sqlalchemy import DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.work import Work


class AccessEvent(Base):
    __tablename__ = "access_events"

    __table_args__ = (
        Index(
            "ix_access_events_work_id_accessed_at",
            "work_id",
            "accessed_at",
        ),
        Index(
            "ix_access_events_accessed_at",
            "accessed_at",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    work_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "works.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    accessed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    work: Mapped["Work"] = relationship(
        back_populates="access_events",
    )
