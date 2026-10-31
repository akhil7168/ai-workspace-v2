from uuid import UUID
from sqlalchemy.orm import Session

from fastapi import HTTPException  # type: ignore[reportMissingImports]

from app.models.project import Project, ProjectStatus
from app.models.project_member import ProjectMember, ProjectRole
from app.repositories.project_repository import ProjectRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectService:
    def __init__(self, db: Session):
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
            raise HTTPException(
                status_code=404,
                detail="Workspace not found",
            )

        if workspace.is_archived:
            raise HTTPException(
                status_code=409,
                detail="Cannot create a project in an archived workspace",
            )

        project = Project(
            title=payload.title,
            description=payload.description,
            workspace_id=workspace.id,
            created_by=current_user_id,
            status=ProjectStatus.ACTIVE,
            visibility="PRIVATE",
        )
        project.memberships.append(
            ProjectMember(
                user_id=current_user_id,
                role=ProjectRole.OWNER,
                assigned_by=current_user_id,
            )
        )

        return self.project_repo.create(project)

    def list_workspace_projects(self, workspace_id: UUID, limit: int | None = None, offset: int = 0):
        workspace = self.workspace_repo.get_by_id(workspace_id)

        if workspace is None:
            raise HTTPException(
                status_code=404,
                detail="Workspace not found",
            )

        if workspace.is_archived:
            raise HTTPException(
                status_code=404,
                detail="Workspace not found",
            )

        return self.project_repo.get_workspace_projects(
            workspace_id,
            limit=limit,
            offset=offset,
        )

    def get_project(self, project_id: UUID):
        project = self.project_repo.get_by_id(project_id)

        if project is None:
            raise HTTPException(
                status_code=404,
                detail="Project not found",
            )

        if project.status == ProjectStatus.ARCHIVED:
            raise HTTPException(
                status_code=404,
                detail="Project not found",
            )

        return project

    def update_project(
        self,
        project_id: UUID,
        payload: ProjectUpdate,
        current_user_id: UUID,
    ):
        project = self.get_project(project_id)

        if payload.title is not None:
            project.title = payload.title

        if payload.description is not None:
            project.description = payload.description

        if payload.status is not None:
            project.status = payload.status

        return self.project_repo.update(project)

    def archive_project(
        self,
        project_id: UUID,
        current_user_id: UUID,
    ):
        project = self.get_project(project_id)

        if project.status == ProjectStatus.ARCHIVED:
            raise HTTPException(
                status_code=409,
                detail="Project is already archived",
            )

        project.status = ProjectStatus.ARCHIVED

        return self.project_repo.update(project)

    def delete_project(
        self,
        project_id: UUID,
        current_user_id: UUID,
    ):
        project = self.get_project(project_id)

        if project.status == ProjectStatus.ARCHIVED:
            raise HTTPException(
                status_code=409,
                detail="Project is already archived",
            )

        project.status = ProjectStatus.ARCHIVED
        self.project_repo.update(project)

        return {
            "message": "Project archived successfully"
        }

    def require_owner(
        self,
        project_id: UUID,
        current_user_id: UUID,
    ):
        project = self.get_project(
            project_id
        )

        if project.created_by != current_user_id:
            raise HTTPException(
                status_code=403,
                detail="Project ownership required",
            )

        return project