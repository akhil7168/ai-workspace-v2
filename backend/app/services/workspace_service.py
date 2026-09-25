from uuid import UUID
from typing import Any, TYPE_CHECKING, TypeAlias

# Keep service type annotations usable when SQLAlchemy is not available to the
# editor/runtime environment.
if TYPE_CHECKING:
    from sqlalchemy.orm import Session as SQLAlchemySession  # type: ignore[reportMissingImports]

    DatabaseSession: TypeAlias = SQLAlchemySession
else:
    DatabaseSession: TypeAlias = Any

try:
    from fastapi import HTTPException  # type: ignore[reportMissingImports]
except ImportError:
    class HTTPException(Exception):
        def __init__(self, status_code: int, detail: str):
            self.status_code = status_code
            self.detail = detail
            super().__init__(detail)
from app.models.workspace import Workspace
from app.models.workspace_member import WorkspaceRole

from app.repositories.workspace_repository import WorkspaceRepository
from app.repositories.user_repository import UserRepository
from app.repositories.workspace_member_repository import WorkspaceMemberRepository

from app.services.workspace_member_service import WorkspaceMemberService

from app.schemas.workspace import WorkspaceCreate, WorkspaceUpdate


class WorkspaceService:

    def __init__(self, db: DatabaseSession):
        self.db = db

        self.workspace_repository = WorkspaceRepository(db)
        self.user_repository = UserRepository(db)
        self.member_repository = WorkspaceMemberRepository(db)

        self.membership_service = WorkspaceMemberService(db)

    # ----------------------------
    # CREATE WORKSPACE
    # ----------------------------
    def create_workspace(
        self,
        payload: WorkspaceCreate,
        owner_id: str,
    ):
        owner = self.user_repository.get_by_id(owner_id)

        if not owner:
            raise ValueError("User not found")

        workspace = Workspace(
            name=payload.name,
            description=payload.description,
            owner_id=owner_id
        )

        workspace = self.workspace_repository.create(workspace)

    # Auto Owner Membership
        self.membership_service.add_member(
            workspace.id,
            owner_id,
            WorkspaceRole.OWNER
        )

        return workspace

    # ----------------------------
    # LIST USER WORKSPACES
    # ----------------------------
    def list_workspaces(self, user_id: str):
        memberships = self.membership_service.get_user_memberships(user_id)

        return [membership.workspace for membership in memberships]

    # ----------------------------
    # GET SINGLE WORKSPACE
    # ----------------------------
    def get_workspace(self, workspace_id: str, user_id: str):

        membership = self.membership_service.get_membership(
            workspace_id,
            user_id,
        )

        if membership is None:
            raise ValueError("Workspace not found")

        return membership.workspace
    # ----------------------------
    # UPDATE WORKSPACE
    # ----------------------------
    def update_workspace(
        self,
        workspace_id: str,
        payload,
        user_id: str,
    ):
        membership = self.membership_service.get_membership(
            workspace_id,
            user_id,
        )

        if membership is None:
            raise ValueError("Workspace not found")

        if membership.role not in (
            WorkspaceRole.OWNER,
            WorkspaceRole.ADMIN,
        ):
            raise PermissionError("Permission denied")

        workspace = membership.workspace

        workspace.name = payload.name
        workspace.description = payload.description

        return self.workspace_repository.update(workspace)

    # ----------------------------
    # DELETE WORKSPACE
    # ----------------------------
    def delete_workspace(
        self,
        workspace_id: str,
        user_id: str,
    ):
        membership = self.membership_service.get_membership(
            workspace_id,
            user_id,
        )

        if membership is None:
            raise ValueError("Workspace not found")

        if membership.role != WorkspaceRole.OWNER:
            raise PermissionError("Only owner can delete workspace")

        self.workspace_repository.delete(membership.workspace)

        return {"message": "Workspace deleted"}


class WorkspaceRole:
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"


    