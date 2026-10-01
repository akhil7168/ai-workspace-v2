from enum import Enum

from app.models.workspace_member import WorkspaceRole


class Permission(str, Enum):
    WORKSPACE_VIEW = "workspace:view"
    WORKSPACE_UPDATE = "workspace:update"
    WORKSPACE_DELETE = "workspace:delete"

    MEMBER_VIEW = "member:view"
    MEMBER_ADD = "member:add"
    MEMBER_UPDATE_ROLE = "member:update_role"
    MEMBER_REMOVE = "member:remove"

    PROJECT_VIEW = "project:view"
    PROJECT_CREATE = "project:create"
    PROJECT_UPDATE = "project:update"
    PROJECT_DELETE = "project:delete"


ROLE_PERMISSIONS = {
    WorkspaceRole.OWNER: {
        Permission.WORKSPACE_VIEW,
        Permission.WORKSPACE_UPDATE,
        Permission.WORKSPACE_DELETE,

        Permission.MEMBER_VIEW,
        Permission.MEMBER_ADD,
        Permission.MEMBER_UPDATE_ROLE,
        Permission.MEMBER_REMOVE,

        Permission.PROJECT_VIEW,
        Permission.PROJECT_CREATE,
        Permission.PROJECT_UPDATE,
        Permission.PROJECT_DELETE,
    },

    WorkspaceRole.ADMIN: {
        Permission.WORKSPACE_VIEW,
        Permission.WORKSPACE_UPDATE,

        Permission.MEMBER_VIEW,
        Permission.MEMBER_ADD,
        Permission.MEMBER_UPDATE_ROLE,
        Permission.MEMBER_REMOVE,

        Permission.PROJECT_VIEW,
        Permission.PROJECT_CREATE,
        Permission.PROJECT_UPDATE,
        Permission.PROJECT_DELETE,
    },

    WorkspaceRole.MEMBER: {
        Permission.WORKSPACE_VIEW,

        Permission.MEMBER_VIEW,

        Permission.PROJECT_VIEW,
        Permission.PROJECT_CREATE,
        Permission.PROJECT_UPDATE,
    },

    WorkspaceRole.VIEWER: {
        Permission.WORKSPACE_VIEW,

        Permission.MEMBER_VIEW,

        Permission.PROJECT_VIEW,
    },
}