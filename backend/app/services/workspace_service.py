from uuid import UUID
from typing import Any

# Keep service type annotations usable when SQLAlchemy is not available to the
# editor/runtime environment.
Session = Any
try:
    from fastapi import HTTPException  # type: ignore[reportMissingImports]
except ImportError:
    class HTTPException(Exception):
        def __init__(self, status_code: int, detail: str):
            self.status_code = status_code
            self.detail = detail
            super().__init__(detail)

from app.models.workspace import Workspace
from app.repositories.workspace_repository import WorkspaceRepository
from app.schemas.workspace import WorkspaceCreate, WorkspaceUpdate


class WorkspaceService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = WorkspaceRepository(db)

    # ----------------------------
    # CREATE WORKSPACE
    # ----------------------------
    def create_workspace(
        self,
        payload: WorkspaceCreate,
        owner_id: UUID,
    ):
        workspace = Workspace(
            name=payload.name,
            description=payload.description,
            color=payload.color,
            owner_id=owner_id,
        )

        return self.repo.create(workspace)

    # ----------------------------
    # LIST USER WORKSPACES
    # ----------------------------
    def list_workspaces(self, owner_id: UUID):
        return self.repo.get_user_workspaces(owner_id)

    # ----------------------------
    # GET SINGLE WORKSPACE
    # ----------------------------
    def get_workspace(self, workspace_id: UUID, owner_id: UUID):
        workspace = self.repo.get_by_id(workspace_id)

        if not workspace:
            raise HTTPException(404, "Workspace not found")

        if workspace.owner_id != owner_id:
            raise HTTPException(403, "Access denied")

        return workspace

    # ----------------------------
    # UPDATE WORKSPACE
    # ----------------------------
    def update_workspace(
        self,
        workspace_id: UUID,
        payload: WorkspaceUpdate,
        owner_id: UUID,
    ):
        workspace = self.get_workspace(workspace_id, owner_id)

        updates = payload.model_dump(exclude_unset=True)

        for key, value in updates.items():
            setattr(workspace, key, value)

        return self.repo.update(workspace)

    # ----------------------------
    # DELETE WORKSPACE
    # ----------------------------
    def delete_workspace(self, workspace_id: UUID, owner_id: UUID):
        workspace = self.get_workspace(workspace_id, owner_id)

        self.repo.delete(workspace)

        return {"message": "Workspace deleted successfully"}