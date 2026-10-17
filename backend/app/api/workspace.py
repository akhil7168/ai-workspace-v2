from app.core.authorization import require_workspace_permission
from app.core.permissions import Permission
from fastapi import APIRouter, Depends, Query  # type: ignore[reportMissingImports]
from uuid import UUID

from sqlalchemy.orm import Session  # type: ignore[reportMissingImports]

from app.db.session import get_db
from app.core.auth import get_current_user
from app.models.user import User

from app.schemas.workspace import (
    WorkspaceCreate,
    WorkspaceUpdate,
    WorkspaceResponse,
)
from app.schemas.common import ErrorResponse, MessageResponse

from app.services.workspace_service import WorkspaceService

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])


@router.post(
    "",
    response_model=WorkspaceResponse,
    summary="Create a workspace",
    description="Create a workspace owned by the authenticated user and initialize that user as an OWNER member.",
    responses={
        401: {"model": ErrorResponse, "description": "Authentication credentials are invalid."},
        404: {"model": ErrorResponse, "description": "The current user was not found."},
    },
)
def create_workspace(
    payload: WorkspaceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return WorkspaceService(db).create_workspace(payload, current_user.id)


@router.get(
    "",
    response_model=list[WorkspaceResponse],
    summary="List the current user's workspaces",
    description="Returns non-archived workspaces the authenticated user belongs to, ordered by limit and offset.",
    responses={
        401: {"model": ErrorResponse, "description": "Authentication credentials are invalid."},
    },
)
def list_workspaces(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    return WorkspaceService(db).list_workspaces(current_user.id, limit=limit, offset=offset)


@router.get(
    "/{workspace_id}",
    response_model=WorkspaceResponse,
    summary="Get a workspace",
    description="Requires workspace membership and the workspace:view permission. Archived or inaccessible workspaces are hidden.",
    responses={
        401: {"model": ErrorResponse, "description": "Authentication credentials are invalid."},
        403: {"model": ErrorResponse, "description": "The member's workspace role does not allow viewing."},
        404: {"model": ErrorResponse, "description": "Workspace is missing, archived, or inaccessible."},
    },
)
def get_workspace(
    workspace_id: UUID,
    db: Session = Depends(get_db),
    membership=Depends(
        require_workspace_permission(
            Permission.WORKSPACE_VIEW
        )
    ),
):
    return WorkspaceService(db).get_workspace(
        workspace_id,
        membership.user_id,
    )

@router.put(
    "/{workspace_id}",
    response_model=WorkspaceResponse,
    summary="Update a workspace",
    description="Requires workspace:update. Only the workspace OWNER can change is_archived; archiving hides the workspace from normal workspace operations.",
    responses={
        401: {"model": ErrorResponse, "description": "Authentication credentials are invalid."},
        403: {"model": ErrorResponse, "description": "The member's role does not allow this change, or the member is not the owner while changing is_archived."},
        404: {"model": ErrorResponse, "description": "Workspace is missing, archived, or inaccessible."},
    },
)
def update_workspace(
    workspace_id: UUID,
    payload: WorkspaceUpdate,
    db: Session = Depends(get_db),
    membership=Depends(
        require_workspace_permission(
            Permission.WORKSPACE_UPDATE
        )
    ),
):
    return WorkspaceService(db).update_workspace(
        workspace_id,
        payload,
        membership.user_id,
    )


@router.delete(
    "/{workspace_id}",
    response_model=MessageResponse,
    summary="Archive a workspace",
    description="Soft-deletes (archives) the workspace. Only its OWNER can do this; the workspace is not physically deleted.",
    responses={
        401: {"model": ErrorResponse, "description": "Authentication credentials are invalid."},
        403: {"model": ErrorResponse, "description": "Workspace OWNER permission is required."},
        404: {"model": ErrorResponse, "description": "Workspace is missing or inaccessible."},
    },
)
def delete_workspace(
    workspace_id: UUID,
    db: Session = Depends(get_db),
    membership=Depends(
        require_workspace_permission(
            Permission.WORKSPACE_DELETE
        )
    ),
):
    return WorkspaceService(db).delete_workspace(
        workspace_id,
        membership.user_id,
    )