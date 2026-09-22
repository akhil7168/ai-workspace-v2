from uuid import uuid4
import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Text, UUID  # type: ignore[import-not-found]
from sqlalchemy.orm import relationship  # type: ignore[import-not-found]
from datetime import datetime, timezone

from app.db.base_class import Base
from enum import Enum


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

    sessions = relationship(
        "UserSession",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    workspaces = relationship(
        "Workspace",
        back_populates="owner",
        cascade="all, delete-orphan",
    )

    projects = relationship(
        "Project",
        back_populates="creator",
        cascade="all, delete-orphan",
    )