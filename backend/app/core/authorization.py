from uuid import UUID

from fastapi import Depends, HTTPException # pyright: ignore[reportMissingImports]
from sqlalchemy.orm import Session # pyright: ignore[reportMissingImports]

from app.core.auth import get_current_user
from app.core.permissions import Permission
from app.db.session import get_db
from app.services.permission_service import PermissionService
from app.services.workspace_member_service import WorkspaceMemberService


def require_workspace_permission(permission: Permission):

    def checker(
        workspace_id: UUID,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user),
    ):
        service = WorkspaceMemberService(db)

        membership = service.get_membership(
            workspace_id,
            current_user.id,
        )

        if membership is None:
            raise HTTPException(
                status_code=403,
                detail="User is not a workspace member",
            )

        PermissionService.require_permission(
            membership.role,
            permission,
        )

        return membership

    return checker

def require_project_permission(permission: Permission):

    def checker(
        project_id: UUID,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user),
    ):
        from app.services.project_service import ProjectService

        project_service = ProjectService(db)

        project = project_service.get_project(
            project_id
        )

        membership_service = WorkspaceMemberService(db)

        membership = membership_service.get_membership(
            project.workspace_id,
            current_user.id,
        )

        if membership is None:
            raise HTTPException(
                status_code=403,
                detail="User is not a workspace member",
            )

        PermissionService.require_permission(
            membership.role,
            permission,
        )

        return membership

    return checker