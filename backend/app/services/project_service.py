from uuid import UUID
from typing import Any
from fastapi import HTTPException # type: ignore

from app.models.project import Project, ProjectStatus
from app.repositories.project_repository import ProjectRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectService:

    def __init__(self, db: Any):
        self.db = db
        self.project_repo = ProjectRepository(db)
        self.workspace_repo = WorkspaceRepository(db)

    def create_project(
        self,
        workspace_id: UUID,
        payload: ProjectCreate,
        current_user_id: UUID,
    ):
        workspace = self.workspace_repo.get_by_id(workspace_id)

        if workspace is None:
            raise HTTPException(404, "Workspace not found")

        project = Project(
            title=payload.title,
            description=payload.description,
            workspace_id=workspace.id,
            created_by=current_user_id,
            status=ProjectStatus.ACTIVE,
        )

        return self.project_repo.create(project)

    def list_workspace_projects(self, workspace_id: UUID):
        workspace = self.workspace_repo.get_by_id(workspace_id)

        if workspace is None:
            raise HTTPException(404, "Workspace not found")

        return self.project_repo.get_workspace_projects(workspace_id)

    def get_project(self, project_id: UUID):
        project = self.project_repo.get_by_id(project_id)

        if project is None:
            raise HTTPException(404, "Project not found")

        return project

    def update_project(
        self,
        project_id: UUID,
        payload: ProjectUpdate,
    ):
        project = self.get_project(project_id)

        if payload.title is not None:
            project.title = payload.title

        if payload.description is not None:
            project.description = payload.description

        if payload.status is not None:
            project.status = payload.status

        return self.project_repo.update(project)

    def archive_project(self, project_id: UUID):
        project = self.get_project(project_id)

        project.status = ProjectStatus.ARCHIVED

        return self.project_repo.update(project)

    def delete_project(self, project_id: UUID):
        project = self.get_project(project_id)
        self.project_repo.delete(project)

        return {"message": "Project deleted successfully"}