from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.repository import RepositoryStatus


class RepositoryConnect(BaseModel):
    url: str = Field(..., min_length=1, max_length=500)


class RepositoryFileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    path: str
    language: str
    size_bytes: int
    content_hash: str
    created_at: datetime


class RepositoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    owner: str
    name: str
    url: str
    branch: Optional[str] = None
    commit_sha: Optional[str] = None
    status: RepositoryStatus
    file_count: int
    total_size_bytes: int
    created_at: datetime
    updated_at: datetime
    indexed_at: Optional[datetime] = None
    error_message: Optional[str] = None


class EmbeddingResponse(BaseModel):
    total_chunks: int
    already_embedded: int
    newly_embedded: int
    failed: int
    model_name: str


class SemanticSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=4000)
    limit: int = Field(default=5, ge=1, le=20)

    @field_validator("query")
    @classmethod
    def validate_query(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Query must not be empty")
        return value


class SemanticSearchResult(BaseModel):
    chunk_id: UUID
    repository_id: UUID
    file_path: str
    symbol: str
    symbol_type: str
    start_line: int
    end_line: int
    language: str
    similarity: float
    snippet: str


class SemanticSearchResponse(BaseModel):
    query: str
    model_name: str
    total: int
    results: list[SemanticSearchResult]
