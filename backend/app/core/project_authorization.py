from uuid import UUID

from fastapi import Depends, HTTPException  # pyright: ignore[reportMissingImports]
from sqlalchemy.orm import Session  # pyright: ignore[reportMissingImports]

from app.core.auth import get_current_user
from app.core.permissions import Permission
from app.db.session import get_db
from app.repositories.project_member_repository import (
    ProjectMemberRepository,
)
from app.repositories.project_repository import ProjectRepository
from app.repositories.workspace_member_repository import (
    WorkspaceMemberRepository,
)
from app.services.permission_service import PermissionService
from app.services.project_service import ProjectService


def require_project_owner(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    project = ProjectService(db).get_project(project_id)

    if project.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Project ownership required",
        )

    return project


def require_project_member_permission(
    permission: Permission,
):

    def checker(
        project_id: UUID,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user),
    ):

        project_repo = ProjectRepository(db)
        workspace_member_repo = WorkspaceMemberRepository(db)
        project_member_repo = ProjectMemberRepository(db)

        # -----------------------------------------------------
        # Project must exist
        # -----------------------------------------------------

        project = project_repo.get_by_id(project_id)

        if project is None:
            raise HTTPException(
                status_code=404,
                detail="Project not found",
            )

        # -----------------------------------------------------
        # Current user must belong to workspace
        # -----------------------------------------------------

        workspace_membership = (
            workspace_member_repo.get_membership(
                workspace_id=project.workspace_id,
                user_id=current_user.id,
            )
        )

        if workspace_membership is None:
            raise HTTPException(
                status_code=403,
                detail="User is not a workspace member",
            )

        # -----------------------------------------------------
        # Current user must belong to project
        # -----------------------------------------------------

        project_membership = project_member_repo.get(
            project_id=project_id,
            user_id=current_user.id,
        )

        if project_membership is None:
            raise HTTPException(
                status_code=403,
                detail="User is not a project member",
            )

        # -----------------------------------------------------
        # Check project role permission
        # -----------------------------------------------------

        PermissionService.require_project_permission(
            project_membership.role,
            permission,
        )

        return project_membership

    return checker