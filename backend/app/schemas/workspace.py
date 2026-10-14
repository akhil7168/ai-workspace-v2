from uuid import UUID
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class WorkspaceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    description: Optional[str] = Field(default=None, max_length=2000)
    color: Optional[str] = Field(default="#6366F1", min_length=1, max_length=32)
    icon: Optional[str] = Field(default="folder", min_length=1, max_length=64)


class WorkspaceUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=120)
    description: Optional[str] = Field(default=None, max_length=2000)
    color: Optional[str] = Field(default=None, min_length=1, max_length=32)
    icon: Optional[str] = Field(default=None, min_length=1, max_length=64)
    is_archived: Optional[bool] = None


class WorkspaceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    owner_id: UUID
    name: str
    description: Optional[str]
    color: str
    icon: str
    is_archived: bool
    created_at: datetime
    updated_at: datetime