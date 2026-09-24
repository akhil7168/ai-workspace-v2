from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, UUID, func  # pyright: ignore[reportMissingImports]
from sqlalchemy.orm import Mapped, mapped_column, relationship  # pyright: ignore[reportMissingImports]

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.workspace import Workspace


# -----------------------------
# Workspace Roles
# -----------------------------
class WorkspaceRole(str, Enum):
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"
    VIEWER = "VIEWER"


# -----------------------------
# Workspace Membership Table
# -----------------------------
class WorkspaceMember(Base):
    __tablename__ = "workspace_members"

    # Composite Primary Key
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        primary_key=True,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )

    role: Mapped[WorkspaceRole] = mapped_column(
        SQLEnum(WorkspaceRole, name="workspace_role_enum"),
        nullable=False,
        default=WorkspaceRole.MEMBER,
    )

    invited_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )

    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # -----------------------------
    # Relationships
    # -----------------------------
    workspace: Mapped["Workspace"] = relationship(
        "Workspace",
        back_populates="members",
        foreign_keys=[workspace_id],
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="workspace_memberships",
        foreign_keys=[user_id],
    )

    inviter: Mapped["User"] = relationship(
        "User",
        foreign_keys=[invited_by],
    )