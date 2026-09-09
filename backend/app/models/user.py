from enum import Enum
import uuid

from sqlalchemy import Boolean, Column, String
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    USER = "USER"
    AGENT = "AGENT"


class User(Base):

    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    full_name = Column(
        String(100),
        nullable=False
    )

    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    hashed_password = Column(
        String(255),
        nullable=False
    )

    is_active = Column(
        Boolean,
        default=True
    )

    role = Column(
        String(20),
        default=UserRole.USER.value,
        nullable=False
    )