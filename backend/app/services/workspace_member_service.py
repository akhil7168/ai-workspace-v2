from typing import Any

class HTTPException(Exception):
    """HTTP error raised by the service layer.

    Kept local so this service does not depend on FastAPI at import time.
    """

    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)

# Keep the service importable when SQLAlchemy is not installed in the
# environment used for static analysis.
Session = Any

from app.models.workspace_member import WorkspaceMember, WorkspaceRole
from app.repositories.workspace_member_repository import WorkspaceMemberRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.repositories.user_repository import UserRepository


class WorkspaceMemberService:

    def __init__(self, db: Session):

        self.db = db

        self.member_repo = WorkspaceMemberRepository(db)
        self.workspace_repo = WorkspaceRepository(db)
        self.user_repo = UserRepository(db)

    def add_member(
        self,
        workspace_id,
        user_id,
        invited_by,
        role: WorkspaceRole,
    ):

        workspace = self.workspace_repo.get_workspace(workspace_id)

        if not workspace:
            raise HTTPException(404, "Workspace not found")

        user = self.user_repo.get_user_by_id(user_id)

        if not user:
            raise HTTPException(404, "User not found")

        existing = self.member_repo.get_membership(workspace_id, user_id)

        if existing:
            raise HTTPException(400, "User already belongs to workspace")

        member = WorkspaceMember(
            workspace_id=workspace_id,
            user_id=user_id,
            invited_by=invited_by,
            role=role,
        )

        return self.member_repo.add_member(member)

    def list_members(self, workspace_id):

        workspace = self.workspace_repo.get_workspace(workspace_id)

        if not workspace:
            raise HTTPException(404, "Workspace not found")

        return self.member_repo.get_workspace_members(workspace_id)

    def remove_member(self, workspace_id, user_id):

        member = self.member_repo.get_membership(workspace_id, user_id)

        if not member:
            raise HTTPException(404, "Member not found")

        if member.role == WorkspaceRole.OWNER:
            raise HTTPException(400, "Owner cannot be removed")

        self.member_repo.remove_member(member)

        return {"message": "Member removed successfully"}

    def update_role(
        self,
        workspace_id,
        user_id,
        role: WorkspaceRole,
    ):

        member = self.member_repo.get_membership(workspace_id, user_id)

        if not member:
            raise HTTPException(404, "Membership not found")

        return self.member_repo.update_role(member, role)

    def require_workspace_member(
        self,
        workspace_id,
        user_id,
    ):

        member = self.member_repo.get_membership(workspace_id, user_id)

        if not member:
            raise HTTPException(
                403,
                "User is not a workspace member",
            )

        return member

    def require_workspace_admin(
        self,
        workspace_id,
        user_id,
    ):

        member = self.require_workspace_member(workspace_id, user_id)

        if member.role not in (
            WorkspaceRole.OWNER,
            WorkspaceRole.ADMIN,
        ):
            raise HTTPException(
                403,
                "Admin permission required",
            )

        return member

    def workspace_size(self, workspace_id):

        return self.member_repo.count_workspace_members(workspace_id)