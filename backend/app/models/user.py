from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, DateTime, String, Text  # pyright: ignore[reportMissingImports]
from sqlalchemy.dialects.postgresql import UUID  # pyright: ignore[reportMissingImports]
from sqlalchemy.orm import Mapped, relationship  # pyright: ignore[reportMissingImports]

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.session import UserSession
    from app.models.workspace_member import WorkspaceMember

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    full_name = Column(String(100), nullable=False)

    email = Column(String(255), unique=True, nullable=False)

    password_hash = Column(String(255), nullable=False)

    role = Column(String(30), default=UserRole.USER.value, nullable=False)

    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    bio = Column(Text, nullable=True)
    avatar_url = Column(String(255), nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    workspace_memberships: Mapped[list["WorkspaceMember"]] = relationship(
        "WorkspaceMember",
        back_populates="user",
        foreign_keys="WorkspaceMember.user_id",
    )

    workspaces = relationship(
        "Workspace",
        secondary="workspace_members",
        back_populates="users",
        viewonly=True,
    )

    projects: Mapped[list["Project"]] = relationship(
        "Project",
        back_populates="owner",
    )

    sessions: Mapped[list["UserSession"]] = relationship(
        "UserSession",
        back_populates="user",
        cascade="all, delete-orphan",
    )