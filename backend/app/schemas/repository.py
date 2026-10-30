from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

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
