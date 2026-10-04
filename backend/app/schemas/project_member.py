from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.project_member import ProjectRole


class ProjectMemberCreate(BaseModel):
    user_id: UUID
    role: ProjectRole = ProjectRole.MEMBER


class ProjectMemberRoleUpdate(BaseModel):
    role: ProjectRole


class ProjectMemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    project_id: UUID
    user_id: UUID
    role: ProjectRole
    assigned_by: UUID | None = None
    joined_at: datetime