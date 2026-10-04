from uuid import UUID

from fastapi import APIRouter, Depends  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from app.core.auth import get_current_user
from app.core.project_authorization import require_project_member_permission
from app.core.permissions import Permission
from app.db.session import get_db
from app.schemas.project_member import (
    ProjectMemberCreate,
    ProjectMemberRoleUpdate,
    ProjectMemberResponse,
)
from app.services.project_member_service import ProjectMemberService


router = APIRouter(
    prefix="/projects",
    tags=["Project Members"],
)


@router.post(
    "/{project_id}/members",
    response_model=ProjectMemberResponse,
)
def add_project_member(
    project_id: UUID,
    payload: ProjectMemberCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
    _permission=Depends(
        require_project_member_permission(
            Permission.PROJECT_MEMBER_ADD
        )
    ),
):
    return ProjectMemberService(db).add_member(
        project_id=project_id,
        payload=payload,
        assigned_by=current_user.id,
    )


@router.get(
    "/{project_id}/members",
    response_model=list[ProjectMemberResponse],
)
def list_project_members(
    project_id: UUID,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
    _permission=Depends(
        require_project_member_permission(
            Permission.PROJECT_MEMBER_VIEW
        )
    ),
):
    return ProjectMemberService(db).list_members(
        project_id=project_id
    )


@router.patch(
    "/{project_id}/members/{user_id}",
    response_model=ProjectMemberResponse,
)
def update_project_member_role(
    project_id: UUID,
    user_id: UUID,
    payload: ProjectMemberRoleUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
    _permission=Depends(
        require_project_member_permission(
            Permission.PROJECT_MEMBER_UPDATE_ROLE
        )
    ),
):
    return ProjectMemberService(db).update_role(
        project_id=project_id,
        user_id=user_id,
        payload=payload,
    )


@router.delete(
    "/{project_id}/members/{user_id}",
)
def remove_project_member(
    project_id: UUID,
    user_id: UUID,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
    _permission=Depends(
        require_project_member_permission(
            Permission.PROJECT_MEMBER_REMOVE
        )
    ),
):
    return ProjectMemberService(db).remove_member(
        project_id=project_id,
        user_id=user_id,
    )