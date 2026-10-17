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
from app.schemas.common import ErrorResponse
from app.services.workspace_member_service import WorkspaceMemberService


router = APIRouter(
    prefix="/memberships",
    tags=["Memberships"],
)


@router.post(
    "/{workspace_id}",
    response_model=MembershipResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a workspace member",
    description="Requires member:add in the workspace. The target user must exist; the OWNER role cannot be granted to another member.",
    responses={
        401: {"model": ErrorResponse, "description": "Authentication credentials are invalid."},
        403: {"model": ErrorResponse, "description": "The member's workspace role does not allow adding members."},
        404: {"model": ErrorResponse, "description": "Workspace or target user is missing or inaccessible."},
        409: {"model": ErrorResponse, "description": "The user is already a workspace member."},
    },
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
    summary="List workspace members",
    description="Requires member:view in the workspace.",
    responses={
        401: {"model": ErrorResponse, "description": "Authentication credentials are invalid."},
        403: {"model": ErrorResponse, "description": "The member's workspace role does not allow viewing members."},
        404: {"model": ErrorResponse, "description": "Workspace is missing or inaccessible."},
    },
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
    summary="Change a workspace member's role",
    description="Requires member:update_role. An existing OWNER cannot be changed and a second OWNER cannot be created.",
    responses={
        400: {"model": ErrorResponse, "description": "Changing the OWNER role or creating another OWNER is not allowed."},
        401: {"model": ErrorResponse, "description": "Authentication credentials are invalid."},
        403: {"model": ErrorResponse, "description": "The member's workspace role does not allow changing roles."},
        404: {"model": ErrorResponse, "description": "Membership or workspace is missing or inaccessible."},
    },
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