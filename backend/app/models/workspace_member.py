import enum
import uuid
from datetime import datetime

from sqlalchemy import Enum, ForeignKey, DateTime  # pyright: ignore[reportMissingImports]
from sqlalchemy.dialects.postgresql import UUID # pyright: ignore[reportMissingImports]
from sqlalchemy.orm import Mapped, mapped_column, relationship # pyright: ignore[reportMissingImports]

from app.db.base import Base


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

    joined_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    workspace = relationship(
        "Workspace",
        back_populates="memberships",
    )

    user = relationship(
        "User",
        back_populates="workspace_memberships",
    )