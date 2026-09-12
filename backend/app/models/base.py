from datetime import datetime, timezone

from sqlalchemy import DateTime  # type: ignore[reportMissingImports]
from sqlalchemy.orm import DeclarativeBase  # type: ignore[reportMissingImports]
from sqlalchemy.orm import Mapped  # type: ignore[reportMissingImports]
from sqlalchemy.orm import mapped_column  # type: ignore[reportMissingImports]


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    """
    Adds created_at and updated_at
    to every database model.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )