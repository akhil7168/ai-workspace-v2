from fastapi import HTTPException # pyright: ignore[reportMissingImports]

from app.core.permissions import Permission, ROLE_PERMISSIONS
from app.models.workspace_member import WorkspaceRole


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