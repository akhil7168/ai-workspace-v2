from uuid import UUID

from fastapi import APIRouter, Depends, status # pyright: ignore[reportMissingImports]
from sqlalchemy.orm import Session # pyright: ignore[reportMissingImports]

from app.core.auth import get_current_user
from app.core.authorization import require_workspace_permission
from app.core.permissions import Permission
from app.db.session import get_db
from app.models.user import User
from app.schemas.membership import (
    MembershipCreate,
    MembershipRoleUpdate,
    MembershipResponse,
)
from app.services.workspace_member_service import WorkspaceMemberService


router = APIRouter(
    prefix="/memberships",
    tags=["Memberships"],
)


@router.post(
    "/{workspace_id}",
    response_model=MembershipResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_member(
    workspace_id: UUID,
    payload: MembershipCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    membership=Depends(
        require_workspace_permission(
            Permission.MEMBER_ADD
        )
    ),
):
    return WorkspaceMemberService(db).add_member(
        workspace_id=workspace_id,
        user_id=payload.user_id,
        role=payload.role,
        invited_by=current_user.id,
    )


@router.get(
    "/{workspace_id}",
    response_model=list[MembershipResponse],
)
def list_members(
    workspace_id: UUID,
    db: Session = Depends(get_db),
    membership=Depends(
        require_workspace_permission(
            Permission.MEMBER_VIEW
        )
    ),
):
    return WorkspaceMemberService(db).list_members(
        workspace_id
    )


@router.patch(
    "/{workspace_id}/{user_id}",
    response_model=MembershipResponse,
)
def update_member_role(
    workspace_id: UUID,
    user_id: UUID,
    payload: MembershipRoleUpdate,
    db: Session = Depends(get_db),
    membership=Depends(
        require_workspace_permission(
            Permission.MEMBER_UPDATE_ROLE
        )
    ),
):
    return WorkspaceMemberService(db).update_member_role(
        workspace_id=workspace_id,
        user_id=user_id,
        new_role=payload.role,
    )