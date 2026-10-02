from app.core.permissions import Permission
from app.models.workspace_member import WorkspaceRole
from app.services.permission_service import PermissionService


def test_owner_can_delete_workspace():
    assert PermissionService.has_permission(
        WorkspaceRole.OWNER,
        Permission.WORKSPACE_DELETE,
    )


def test_admin_cannot_delete_workspace():
    assert not PermissionService.has_permission(
        WorkspaceRole.ADMIN,
        Permission.WORKSPACE_DELETE,
    )


def test_member_cannot_add_member():
    assert not PermissionService.has_permission(
        WorkspaceRole.MEMBER,
        Permission.MEMBER_ADD,
    )


def test_viewer_can_view_workspace():
    assert PermissionService.has_permission(
        WorkspaceRole.VIEWER,
        Permission.WORKSPACE_VIEW,
    )


def test_member_can_create_project():
    assert PermissionService.has_permission(
        WorkspaceRole.MEMBER,
        Permission.PROJECT_CREATE,
    )


def test_viewer_cannot_create_project():
    assert not PermissionService.has_permission(
        WorkspaceRole.VIEWER,
        Permission.PROJECT_CREATE,
    )