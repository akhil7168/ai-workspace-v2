import enum
import uuid
import json
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text, Uuid, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from sqlalchemy.types import TypeDecorator

from app.db.base_class import Base


class EmbeddingVector(TypeDecorator):
    """Use pgvector on PostgreSQL and a JSON-compatible column for SQLite tests."""

    impl = Text
    cache_ok = True

    def __init__(self, dimensions=384):
        super().__init__()
        self.dimensions = dimensions

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            from pgvector.sqlalchemy import Vector
            return dialect.type_descriptor(Vector(self.dimensions))
        return dialect.type_descriptor(Text())

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql":
            return value
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "sqlite" and isinstance(value, str):
            return json.loads(value)
        return value


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
    chunks = relationship("CodeChunk", back_populates="file", cascade="all, delete-orphan")


class CodeChunk(Base):
    __tablename__ = "code_chunks"
    __table_args__ = (
        UniqueConstraint("file_id", "chunk_index", name="uq_code_chunk_file_index"),
        Index("ix_code_chunks_file_id_chunk_index", "file_id", "chunk_index"),
    )

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    file_id = Column(Uuid(as_uuid=True), ForeignKey("repository_files.id", ondelete="CASCADE"), nullable=False, index=True)
    symbol = Column(String(255), nullable=False)
    symbol_type = Column(String(50), nullable=False)
    parent_symbol = Column(String(255), nullable=True)
    start_line = Column(Integer, nullable=False)
    end_line = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    language = Column(String(50), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    embedding = Column(EmbeddingVector(384), nullable=True)
    embedding_model = Column(String(255), nullable=True)
    embedding_status = Column(String(20), nullable=True)
    embedded_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(), onupdate=lambda: datetime.now(), nullable=False)

    file = relationship("RepositoryFile", back_populates="chunks")
