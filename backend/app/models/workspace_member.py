import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey # pyright: ignore[reportMissingImports]
from sqlalchemy.dialects.postgresql import UUID # pyright: ignore[reportMissingImports]
from sqlalchemy.orm import Mapped, mapped_column, relationship # pyright: ignore[reportMissingImports]

from app.db.base_class import Base


if TYPE_CHECKING:
    from app.models.user import User
    from app.models.workspace import Workspace


class WorkspaceRole(str, enum.Enum):
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"
    VIEWER = "VIEWER"


class WorkspaceMember(Base):
    __tablename__ = "workspace_members"

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
        Enum(
            WorkspaceRole,
            name="workspace_role",
            create_type=True,
        ),
        default=WorkspaceRole.MEMBER,
        nullable=False,
    )

    invited_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    joined_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    workspace = relationship(
        "Workspace",
        back_populates="memberships",
        foreign_keys=[workspace_id],
    )

    user = relationship(
        "User",
        back_populates="workspace_memberships",
        foreign_keys=[user_id],
    )

    inviter = relationship(
        "User",
        foreign_keys=[invited_by],
    )