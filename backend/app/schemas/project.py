from uuid import UUID
from typing import Optional
from datetime import datetime
from pydantic import BaseModel

from app.models.project import ProjectStatus


class ProjectCreate(BaseModel):
    title: str
    description: Optional[str] = None


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None


class ProjectResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    status: ProjectStatus

    workspace_id: UUID
    created_by: UUID

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True