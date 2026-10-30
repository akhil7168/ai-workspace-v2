import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text, Uuid, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class RepositoryStatus(str, enum.Enum):
    PENDING = "PENDING"
    INGESTING = "INGESTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Repository(Base):
    __tablename__ = "repositories"
    __table_args__ = (
        UniqueConstraint("project_id", "url", name="uq_repository_project_url"),
    )

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    project_id = Column(Uuid(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    owner = Column(String(100), nullable=False)
    name = Column(String(255), nullable=False)
    url = Column(String(500), nullable=False, index=True)
    branch = Column(String(255), nullable=True)
    commit_sha = Column(String(40), nullable=True)
    status = Column(Enum(RepositoryStatus, name="repository_status"), nullable=False, default=RepositoryStatus.PENDING)
    file_count = Column(Integer, nullable=False, default=0)
    total_size_bytes = Column(Integer, nullable=False, default=0)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(), onupdate=lambda: datetime.now(), nullable=False)
    indexed_at = Column(DateTime(timezone=True), nullable=True)

    files = relationship("RepositoryFile", back_populates="repository", cascade="all, delete-orphan")


class RepositoryFile(Base):
    __tablename__ = "repository_files"
    __table_args__ = (
        UniqueConstraint("repository_id", "path", name="uq_repository_file_path"),
    )

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    repository_id = Column(Uuid(as_uuid=True), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False, index=True)
    path = Column(String(2048), nullable=False)
    language = Column(String(50), nullable=False)
    size_bytes = Column(Integer, nullable=False)
    content_hash = Column(String(64), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(), onupdate=lambda: datetime.now(), nullable=False)

    repository = relationship("Repository", back_populates="files")
