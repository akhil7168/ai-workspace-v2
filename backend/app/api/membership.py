from uuid import UUID

from fastapi import APIRouter, Depends, status # pyright: ignore[reportMissingImports]

from sqlalchemy.orm import Session # pyright: ignore[reportMissingImports]

from app.db.session import get_db
from app.schemas.workspace import (
    WorkspaceCreate,
    WorkspaceUpdate
)
from app.services.workspace_member_service import WorkspaceMemberService
from app.core.auth import get_current_user

router = APIRouter(prefix="/memberships", tags=["Memberships"])

@router.post("/{workspace_id}", status_code=status.HTTP_201_CREATED)
def add_member(
    workspace_id: UUID,
    payload: WorkspaceCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return WorkspaceMemberService(db).add_member(
        workspace_id=workspace_id,
        user_id=payload.user_id,
        role=payload.role
    )

@router.get("/{workspace_id}")
def list_members(
    workspace_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return WorkspaceMemberService(db).list_members(workspace_id)

@router.patch("/{workspace_id}/{user_id}")
def update_member_role(
    workspace_id: UUID,
    user_id: UUID,
    payload: WorkspaceUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return WorkspaceMemberService(db).update_role(
        workspace_id=workspace_id,
        user_id=user_id,
        role=payload.role
    )

@router.delete("/{workspace_id}/{user_id}")
def remove_member(
    workspace_id: UUID,
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    WorkspaceMemberService(db).remove_member(
        workspace_id=workspace_id,
        user_id=user_id
    )

    return {
        "message":"Member removed successfully."
    }