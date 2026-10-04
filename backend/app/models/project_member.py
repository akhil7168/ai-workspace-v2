from uuid import uuid4
import enum

from sqlalchemy import Column, ForeignKey, Enum, DateTime, Uuid  # type: ignore[import-not-found]
from sqlalchemy import orm  # type: ignore[import-not-found]
from sqlalchemy import func  # type: ignore[import-not-found]

from app.db.base_class import Base


class ProjectRole(str, enum.Enum):
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"
    VIEWER = "VIEWER"


class ProjectMember(Base):
    __tablename__ = "project_members"

    project_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        primary_key=True,
    )

    user_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )

    role = Column(
        Enum(ProjectRole),
        nullable=False,
        default=ProjectRole.MEMBER,
    )

    assigned_by = Column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    joined_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    project = orm.relationship(
        "Project",
        back_populates="memberships",
    )

    user = orm.relationship(
        "User",
        foreign_keys=[user_id],
    )

    assigned_by_user = orm.relationship(
        "User",
        foreign_keys=[assigned_by],
    )