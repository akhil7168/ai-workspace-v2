# pyright: reportMissingImports=false
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.auth import get_current_user
from app.core.authorization import (
    require_project_permission,
    require_workspace_permission,
)
from app.core.permissions import Permission

from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
)
from app.schemas.common import ErrorResponse, MessageResponse
from app.services.project_service import ProjectService


router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)


@router.post(
    "/workspace/{workspace_id}",
    response_model=ProjectResponse,
    summary="Create a project in a workspace",
    description="Requires project:create on the workspace. The creator is initialized as ProjectRole.OWNER; that project role does not replace workspace-level authorization for project operations.",
    responses={
        401: {"model": ErrorResponse, "description": "Authentication credentials are invalid."},
        403: {"model": ErrorResponse, "description": "The user's workspace role does not allow project creation."},
        404: {"model": ErrorResponse, "description": "Workspace is missing or inaccessible."},
    },
)
def create_project(
    workspace_id: UUID,
    payload: ProjectCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
    _permission=Depends(
        require_workspace_permission(Permission.PROJECT_CREATE)
    ),
):
    return ProjectService(db).create_project(
        workspace_id=workspace_id,
        payload=payload,
        current_user_id=current_user.id,
    )


@router.get(
    "/workspace/{workspace_id}",
    response_model=list[ProjectResponse],
    summary="List projects in a workspace",
    description="Requires project:view on the workspace. Supports limit (1-100) and offset pagination.",
    responses={
        401: {"model": ErrorResponse, "description": "Authentication credentials are invalid."},
        403: {"model": ErrorResponse, "description": "The user's workspace role does not allow viewing projects."},
        404: {"model": ErrorResponse, "description": "Workspace is missing, archived, or inaccessible."},
    },
)
def list_projects(
    workspace_id: UUID,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
    _permission=Depends(
        require_workspace_permission(Permission.PROJECT_VIEW)
    ),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    return ProjectService(db).list_workspace_projects(
        workspace_id,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Get a project",
    description="Requires workspace membership and project:view for the project's workspace. Archived or inaccessible projects are hidden.",
    responses={
        401: {"model": ErrorResponse, "description": "Authentication credentials are invalid."},
        403: {"model": ErrorResponse, "description": "The user is not a workspace member or lacks project:view."},
        404: {"model": ErrorResponse, "description": "Project is missing or archived."},
    },
)
def get_project(
    project_id: UUID,
    db: Session = Depends(get_db),
    _permission=Depends(
        require_project_permission(Permission.PROJECT_VIEW)
    ),
):
    return ProjectService(db).get_project(project_id)


@router.put(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Update a project",
    description="Requires project:update from the user's workspace role. Project status can be changed through this request.",
    responses={
        401: {"model": ErrorResponse, "description": "Authentication credentials are invalid."},
        403: {"model": ErrorResponse, "description": "The user is not a workspace member or lacks project:update."},
        404: {"model": ErrorResponse, "description": "Project is missing or archived."},
    },
)
def update_project(
    project_id: UUID,
    payload: ProjectUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
    _permission=Depends(
        require_project_permission(Permission.PROJECT_UPDATE)
    ),
):
    return ProjectService(db).update_project(
        project_id=project_id,
        payload=payload,
        current_user_id=current_user.id,
    )


@router.patch(
    "/{project_id}/archive",
    response_model=ProjectResponse,
    summary="Archive a project",
    description="Sets the project status to ARCHIVED; this is a soft deletion. Requires project:update from the workspace role.",
    responses={
        401: {"model": ErrorResponse, "description": "Authentication credentials are invalid."},
        403: {"model": ErrorResponse, "description": "The user is not a workspace member or lacks project:update."},
        404: {"model": ErrorResponse, "description": "Project is missing or already archived."},
    },
)
def archive_project(
    project_id: UUID,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
    _permission=Depends(
        require_project_permission(Permission.PROJECT_UPDATE)
    ),
):
    return ProjectService(db).archive_project(
        project_id=project_id,
        current_user_id=current_user.id,
    )


@router.delete(
    "/{project_id}",
    response_model=MessageResponse,
    summary="Archive a project",
    description="Soft-deletes the project by setting status to ARCHIVED; it does not physically delete the record. Requires project:delete from the workspace role.",
    responses={
        401: {"model": ErrorResponse, "description": "Authentication credentials are invalid."},
        403: {"model": ErrorResponse, "description": "The user is not a workspace member or lacks project:delete."},
        404: {"model": ErrorResponse, "description": "Project is missing or archived."},
    },
)
def delete_project(
    project_id: UUID,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
    _permission=Depends(
        require_project_permission(Permission.PROJECT_DELETE)
    ),
):
    return ProjectService(db).delete_project(
        project_id=project_id,
        current_user_id=current_user.id,
    )