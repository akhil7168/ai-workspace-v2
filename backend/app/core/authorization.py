from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.permissions import Permission
from app.db.session import get_db
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

        if not membership:
            raise HTTPException(
                status_code=403,
                detail="User is not a workspace member",
            )

        from app.services.permission_service import PermissionService

        PermissionService.require_permission(
            membership.role,
            permission,
        )

        return membership

    return checker