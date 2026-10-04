from uuid import UUID

from fastapi import HTTPException  # pyright: ignore[reportMissingImports]
from sqlalchemy.orm import Session  # pyright: ignore[reportMissingImports]

from app.models.project_member import ProjectMember, ProjectRole
from app.repositories.project_member_repository import (
    ProjectMemberRepository,
)
from app.repositories.project_repository import ProjectRepository
from app.repositories.user_repository import UserRepository
from app.repositories.workspace_member_repository import (
    WorkspaceMemberRepository,
)
from app.schemas.project_member import (
    ProjectMemberCreate,
    ProjectMemberRoleUpdate,
)


class ProjectMemberService:

    def __init__(self, db: Session):
        self.db = db

        self.project_member_repo = ProjectMemberRepository(db)
        self.project_repo = ProjectRepository(db)
        self.user_repo = UserRepository(db)
        self.workspace_member_repo = WorkspaceMemberRepository(db)

    # ---------------------------------------------------------
    # Add project member
    # ---------------------------------------------------------

    def add_member(
        self,
        project_id: UUID,
        payload: ProjectMemberCreate,
        assigned_by: UUID,
    ):
        project = self.project_repo.get_by_id(project_id)

        if project is None:
            raise HTTPException(
                status_code=404,
                detail="Project not found",
            )

        user = self.user_repo.get_by_id(payload.user_id)

        if user is None:
            raise HTTPException(
                status_code=404,
                detail="User not found",
            )

        # Target user must belong to the project's workspace
        workspace_membership = (
            self.workspace_member_repo.get_membership(
                workspace_id=project.workspace_id,
                user_id=payload.user_id,
            )
        )

        if workspace_membership is None:
            raise HTTPException(
                status_code=403,
                detail="User is not a workspace member",
            )

        existing = self.project_member_repo.get(
            project_id=project_id,
            user_id=payload.user_id,
        )

        if existing is not None:
            raise HTTPException(
                status_code=409,
                detail="User is already a project member",
            )

        # Only one project OWNER is allowed
        if payload.role == ProjectRole.OWNER:
            members = self.project_member_repo.get_project_members(
                project_id
            )

            owner_exists = any(
                member.role == ProjectRole.OWNER
                for member in members
            )

            if owner_exists:
                raise HTTPException(
                    status_code=400,
                    detail="A second project owner cannot be created",
                )

        member = ProjectMember(
            project_id=project_id,
            user_id=payload.user_id,
            role=payload.role,
            assigned_by=assigned_by,
        )

        return self.project_member_repo.create(member)

    # ---------------------------------------------------------
    # List project members
    # ---------------------------------------------------------

    def list_members(self, project_id: UUID):
        project = self.project_repo.get_by_id(project_id)

        if project is None:
            raise HTTPException(
                status_code=404,
                detail="Project not found",
            )

        return self.project_member_repo.get_project_members(
            project_id
        )

    # ---------------------------------------------------------
    # Update project member role
    # ---------------------------------------------------------

    def update_role(
        self,
        project_id: UUID,
        user_id: UUID,
        payload: ProjectMemberRoleUpdate,
    ):
        project = self.project_repo.get_by_id(project_id)

        if project is None:
            raise HTTPException(
                status_code=404,
                detail="Project not found",
            )

        member = self.project_member_repo.get(
            project_id=project_id,
            user_id=user_id,
        )

        if member is None:
            raise HTTPException(
                status_code=404,
                detail="Project member not found",
            )

        # Existing owner cannot be downgraded
        if member.role == ProjectRole.OWNER:
            raise HTTPException(
                status_code=403,
                detail="Project owner role cannot be changed",
            )

        # Cannot create a second owner
        if payload.role == ProjectRole.OWNER:
            raise HTTPException(
                status_code=400,
                detail="A second project owner cannot be created",
            )

        member.role = payload.role

        return self.project_member_repo.update(member)

    # ---------------------------------------------------------
    # Remove project member
    # ---------------------------------------------------------

    def remove_member(
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

        member = self.project_member_repo.get(
            project_id=project_id,
            user_id=user_id,
        )

        if member is None:
            raise HTTPException(
                status_code=404,
                detail="Project member not found",
            )

        # Owner cannot be removed
        if member.role == ProjectRole.OWNER:
            raise HTTPException(
                status_code=403,
                detail="Project owner cannot be removed",
            )

        self.project_member_repo.delete(member)

        return {
            "message": "Project member removed successfully"
        }