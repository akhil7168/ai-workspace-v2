from uuid import uuid4
from enum import Enum

from sqlalchemy import Column, String, Text, ForeignKey, DateTime, UUID  # type: ignore[reportMissingImports]
from sqlalchemy.orm import relationship  # type: ignore[reportMissingImports]
from sqlalchemy import func  # type: ignore[reportMissingImports]

from app.db.base_class import Base

# ----------------------------------------
# Project Status Enum
# ----------------------------------------
class ProjectStatus(str, Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"


# ----------------------------------------
# Project Visibility Enum
# ----------------------------------------
class ProjectVisibility(str, Enum):
    PRIVATE = "PRIVATE"
    SHARED = "SHARED"


# ----------------------------------------
# Project Model
# ----------------------------------------
class Project(Base):
    __tablename__ = "projects"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    workspace_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )

    created_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    title = Column(
        String(150),
        nullable=False,
    )

    description = Column(
        Text,
        nullable=True,
    )

    status = Column(
        String(20),
        default=ProjectStatus.ACTIVE.value,
        nullable=False,
    )

    visibility = Column(
        String(20),
        default=ProjectVisibility.PRIVATE.value,
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    workspace = relationship(
        "Workspace",
        back_populates="projects",
    )

    creator = relationship(
        "User",
        back_populates="projects",
    )