import uuid

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Uuid, func  # pyright: ignore[reportMissingImports]
from sqlalchemy.orm import relationship  # pyright: ignore[reportMissingImports]
from app.db.base_class import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User

class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    refresh_token = Column(String, nullable=False, unique=True)

    user_agent = Column(String, nullable=True)

    ip_address = Column(String, nullable=True)

    expires_at = Column(DateTime(timezone=True), nullable=False)

    is_revoked = Column(Boolean, default=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationship to User
    user = relationship(
        "User",
        back_populates="sessions",
    )