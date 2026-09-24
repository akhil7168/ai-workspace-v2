from uuid import uuid4
import enum

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum, Uuid  # pyright: ignore[reportMissingImports]
from sqlalchemy.orm import relationship  # pyright: ignore[reportMissingImports]
from sqlalchemy import func  # pyright: ignore[reportMissingImports]

from app.db.base_class import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.workspace import Workspace


class ProjectStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"


class Project(Base):
    __tablename__ = "projects"

    # PRIMARY KEY
    id = Column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
        nullable=False
    )

    title = Column(String(120), nullable=False)

    description = Column(Text)

    status = Column(
        Enum(ProjectStatus),
        nullable=False,
        default=ProjectStatus.ACTIVE
    )

    workspace_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False
    )

    created_by = Column(
        Uuid(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    workspace = relationship(
        "Workspace",
        back_populates="projects"
    )

    owner = relationship(
        "User",
        back_populates="projects"
    )