from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends  # type: ignore[import-not-found]
from sqlalchemy.orm import Session  # type: ignore[import-not-found]

from app.core.auth import get_current_active_user
from app.db.session import get_db
from app.models.user import User

from app.schemas.workspace import (
    WorkspaceCreate,
    WorkspaceUpdate,
    WorkspaceResponse,
)

from app.services.workspace_service import WorkspaceService

router = APIRouter(
    prefix="/workspaces",
    tags=["Workspaces"],
)

@router.post(
    "",
    response_model=WorkspaceResponse,
)
def create_workspace(
    payload: WorkspaceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return WorkspaceService(db).create_workspace(
        owner_id=current_user.id,
        payload=payload,
    )

@router.get(
    "",
    response_model=List[WorkspaceResponse],
)
def list_workspaces(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return WorkspaceService(db).list_workspaces(
        owner_id=current_user.id
    )

@router.get(
    "/{workspace_id}",
    response_model=WorkspaceResponse,
)
def get_workspace(
    workspace_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return WorkspaceService(db).get_workspace(
        workspace_id=workspace_id,
        owner_id=current_user.id,
    )

@router.put(
    "/{workspace_id}",
    response_model=WorkspaceResponse,
)
def update_workspace(
    workspace_id: UUID,
    payload: WorkspaceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return WorkspaceService(db).update_workspace(
        workspace_id=workspace_id,
        owner_id=current_user.id,
        payload=payload,
    )

@router.patch(
    "/{workspace_id}/archive",
    response_model=WorkspaceResponse,
)
def archive_workspace(
    workspace_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return WorkspaceService(db).archive_workspace(
        workspace_id=workspace_id,
        owner_id=current_user.id,
    )

@router.delete("/{workspace_id}")
def delete_workspace(
    workspace_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return WorkspaceService(db).delete_workspace(
        workspace_id=workspace_id,
        owner_id=current_user.id,
    )