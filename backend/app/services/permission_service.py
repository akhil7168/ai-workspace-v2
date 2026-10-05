from fastapi import HTTPException  # type: ignore[reportMissingImports]

from app.core.permissions import (
    Permission,
    ROLE_PERMISSIONS,
    PROJECT_ROLE_PERMISSIONS,
)

from app.models.workspace_member import WorkspaceRole
from app.models.project_member import ProjectRole


class PermissionService:

    @staticmethod
    def has_permission(
        role: WorkspaceRole,
        permission: Permission,
    ) -> bool:

        return permission in ROLE_PERMISSIONS.get(
            role,
            set(),
        )

    @staticmethod
    def require_permission(
        role: WorkspaceRole,
        permission: Permission,
    ):
        if not PermissionService.has_permission(
            role,
            permission,
        ):
            raise HTTPException(
                status_code=403,
                detail="Permission denied",
            )

    @staticmethod
    def has_project_permission(
        role: ProjectRole,
        permission: Permission,
    ) -> bool:

        return permission in PROJECT_ROLE_PERMISSIONS.get(
            role,
            set(),
        )

    @staticmethod
    def require_project_permission(
        role: ProjectRole,
        permission: Permission,
    ):
        if not PermissionService.has_project_permission(
            role,
            permission,
        ):
            raise HTTPException(
                status_code=403,
                detail="Project permission denied",
            )