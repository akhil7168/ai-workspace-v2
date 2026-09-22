from uuid import UUID
from typing import Any
from importlib import import_module
from app.repositories.workspace_repository import WorkspaceRepository
from app.repositories.project_repository import ProjectRepository
from app.api import workspace

HTTPException = import_module("fastapi").HTTPException

from app.models.project import Project
from app.repositories.project_repository import ProjectRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
)




class ProjectService:
    def __init__(self, db: Any):
        self.db = db
        self.project_repo = ProjectRepository(db)
        self.workspace_repo = WorkspaceRepository(db)

    def create_project(
        self,
        workspace_id: UUID,
        user_id: UUID,
        payload: ProjectCreate,
    ):
        workspace = self.workspace_repo.get_by_id(workspace_id)

        if workspace is None:
            raise HTTPException(
                status_code=404,
                detail="Workspace not found",
            )

        if workspace.owner_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="You do not own this workspace",
            )

        project = Project(
            workspace_id=workspace_id,
            created_by=user_id,
            name=payload.name,
            description=payload.description,
        )

        return self.project_repo.create(project)

    def list_projects(
        self,
        workspace_id: UUID,
        user_id: UUID,
    ):
        workspace = self.workspace_repo.get_by_id(workspace_id)

        if workspace is None:
            raise HTTPException(
                status_code=404,
                detail="Workspace not found",
            )

        if workspace.owner_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="Access denied",
            )

        return self.project_repo.get_workspace_projects(workspace_id)

    def get_project(
        self,
        project_id: UUID,
        user_id: UUID,
    ):
        project = self.project_repo.get_by_id(project_id)

        if project is None:
            raise HTTPException(
                status_code=404,
                detail="Project not found",
            )

        workspace = self.workspace_repo.get_by_id(project.workspace_id)

        if workspace.owner_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="Access denied",
            )

        return project

    def update_project(
        self,
        project_id: UUID,
        user_id: UUID,
        payload: ProjectUpdate,
    ):
        project = self.get_project(project_id, user_id)

        updates = payload.model_dump(exclude_unset=True)

        for key, value in updates.items():
            setattr(project, key, value)

        return self.project_repo.update(project)