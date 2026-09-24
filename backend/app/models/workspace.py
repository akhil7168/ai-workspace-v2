from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, UUID  # type: ignore[reportMissingImports]
from sqlalchemy.orm import Mapped, relationship  # type: ignore[reportMissingImports]

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.project import Project
    from app.models.workspace_member import WorkspaceMember

class Workspace(Base):
    __tablename__ = "workspaces"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    owner_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    name = Column(
        String,
        nullable=False,
    )

    description = Column(
        String,
        nullable=True,
    )

    color = Column(
        String,
        default="#6366F1",
    )

    icon = Column(
        String,
        default="folder",
    )

    is_archived = Column(
        Boolean,
        default=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    owner: Mapped["User"] = relationship(
        "User",
        back_populates="owned_workspaces",
        foreign_keys=[owner_id],
    )

    members: Mapped[list["WorkspaceMember"]] = relationship(
        "WorkspaceMember",
        back_populates="workspace",
        cascade="all, delete-orphan",
    )

    projects = relationship(
        "Project",
        back_populates="workspace",
        cascade="all, delete-orphan",
    )