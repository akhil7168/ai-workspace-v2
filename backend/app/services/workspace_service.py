from uuid import UUID
from typing import Any, TYPE_CHECKING, TypeAlias

from app.schemas import membership

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

    def create_workspace(
        self,
        payload: WorkspaceCreate,
        owner_id: str,
    ):
        owner = self.user_repository.get_by_id(owner_id)

        if not owner:
            raise HTTPException(
                status_code=404,
                detail="User not found",
            )

        workspace = Workspace(
            name=payload.name,
            description=payload.description,
            owner_id=owner_id,
            color=payload.color or "#6366F1",
            icon=payload.icon or "folder",
        )

        workspace = self.workspace_repository.create(workspace)
        self.membership_service.add_member(
            workspace.id,
            owner_id,
            WorkspaceRole.OWNER,
        )

        return workspace

    def list_workspaces(self, user_id: str, limit: int | None = None, offset: int = 0):
        memberships = self.membership_service.get_user_memberships(user_id, limit=limit, offset=offset)

        return [membership.workspace for membership in memberships if membership.workspace and not membership.workspace.is_archived]

    def get_workspace(self, workspace_id: str, user_id: str):
        membership = self.membership_service.get_membership(
            workspace_id,
            user_id,
        )

        if membership is None:
            raise HTTPException(
                status_code=404,
                detail="Workspace not found",
            )

        if membership.workspace.is_archived:
            raise HTTPException(
                status_code=404,
                detail="Workspace not found",
            )

        return membership.workspace

    def update_workspace(
        self,
        workspace_id: str,
        payload: WorkspaceUpdate,
        user_id: str,
    ):
        membership = self.membership_service.get_membership(
            workspace_id,
            user_id,
        )

        if membership is None:
            raise HTTPException(
                status_code=404,
                detail="Workspace not found",
            )

        workspace = membership.workspace

        if workspace.is_archived:
            raise HTTPException(
                status_code=404,
                detail="Workspace not found",
            )

        if payload.is_archived is not None:
            if membership.role != WorkspaceRole.OWNER:
                raise HTTPException(
                    status_code=403,
                    detail="Only owner can archive workspace",
                )
            workspace.is_archived = payload.is_archived

        if payload.name is not None:
            workspace.name = payload.name

        if payload.description is not None:
            workspace.description = payload.description

        if payload.color is not None:
            workspace.color = payload.color

        if payload.icon is not None:
            workspace.icon = payload.icon

        return self.workspace_repository.update(workspace)

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
            raise HTTPException(status_code=404, detail="Workspace not found")

        if membership.role != WorkspaceRole.OWNER:
            raise HTTPException(
                status_code=403,
                detail="Only owner can delete workspace",
            )

        workspace = membership.workspace

        if workspace.is_archived:
            raise HTTPException(
                status_code=409,
                detail="Workspace is already archived",
            )

        workspace.is_archived = True
        self.workspace_repository.update(workspace)

        return {"message": "Workspace archived successfully"}



    