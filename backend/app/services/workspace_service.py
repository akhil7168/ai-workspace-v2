from uuid import UUID
from typing import Any

from app.models.workspace import Workspace
from app.schemas.workspace import WorkspaceCreate


class WorkspaceService:
    def __init__(self, db: Any):
        self.db = db              # ✅ THIS WAS MISSING

    # -----------------------------
    # Create Workspace
    # -----------------------------
    def create_workspace(
        self,
        owner_id: UUID,
        payload: WorkspaceCreate,
    ):
        workspace = Workspace(
            name=payload.name,
            description=payload.description,
            color=payload.color,
            owner_id=owner_id,
        )

        self.db.add(workspace)
        self.db.commit()
        self.db.refresh(workspace)

        return workspace

    # -----------------------------
    # Get All Workspaces of User
    # -----------------------------
    def get_user_workspaces(
        self,
        owner_id: UUID,
    ):
        return (
            self.db.query(Workspace)
            .filter(Workspace.owner_id == owner_id)
            .order_by(Workspace.created_at.desc())
            .all()
        )

    # -----------------------------
    # Get Workspace by ID
    # -----------------------------
    def get_workspace(
        self,
        workspace_id: UUID,
        owner_id: UUID,
    ):
        return (
            self.db.query(Workspace)
            .filter(
                Workspace.id == workspace_id,
                Workspace.owner_id == owner_id,
            )
            .first()
        )