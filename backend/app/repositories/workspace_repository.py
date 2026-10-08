from uuid import UUID
from sqlalchemy import Session

from app.models.workspace import Workspace


class WorkspaceRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, workspace):
        self.db.add(workspace)
        self.db.commit()
        self.db.refresh(workspace)
        return workspace

    def get_by_id(self, workspace_id: UUID):
        return (
            self.db.query(Workspace)
            .filter(Workspace.id == workspace_id)
            .first()
        )

    def get_user_workspaces(self, owner_id: UUID):
        return (
            self.db.query(Workspace)
            .filter(
                Workspace.owner_id == owner_id,
                Workspace.is_archived == False,
            )
            .order_by(Workspace.created_at.desc())
            .all()
        )

    def update(self, workspace: Workspace):
        self.db.commit()
        self.db.refresh(workspace)
        return workspace

    def delete(self, workspace: Workspace):
        self.db.delete(workspace)
        self.db.commit()