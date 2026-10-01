from app.core.authorization import require_workspace_permission
from app.core.permissions import Permission
from fastapi import APIRouter, Depends  # type: ignore[reportMissingImports]
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

from app.services.workspace_service import WorkspaceService

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])


@router.post("", response_model=WorkspaceResponse)
def create_workspace(
    payload: WorkspaceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return WorkspaceService(db).create_workspace(payload, current_user.id)


@router.get("", response_model=list[WorkspaceResponse])
def list_workspaces(
    db: Session = Depends(get_db),
    membership=Depends(
        require_workspace_permission(Permission.WORKSPACE_VIEW)
    ),
    current_user: User = Depends(get_current_user),
):
    return WorkspaceService(db).list_workspaces(current_user.id)


@router.get(
    "/{workspace_id}",
    response_model=WorkspaceResponse,
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


@router.delete("/{workspace_id}")
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