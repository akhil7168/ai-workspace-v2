from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.workspace_member import WorkspaceRole


class MembershipCreate(BaseModel):
    user_id: UUID
    role: WorkspaceRole = WorkspaceRole.MEMBER


class MembershipRoleUpdate(BaseModel):
    role: WorkspaceRole


class MembershipResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    workspace_id: UUID
    user_id: UUID
    role: WorkspaceRole
    invited_by: UUID | None = None
    joined_at: datetime