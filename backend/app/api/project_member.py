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
from app.schemas.common import ErrorResponse, MessageResponse
from app.services.project_member_service import ProjectMemberService


router = APIRouter(
    prefix="/projects",
    tags=["Project Members"],
)


@router.post(
    "/{project_id}/members",
    response_model=ProjectMemberResponse,
    summary="Add a project member",
    description="Requires the caller to belong to the workspace and project, with project OWNER or ADMIN role. The target user must already belong to the workspace.",
    responses={
        400: {"model": ErrorResponse, "description": "A second project OWNER cannot be created."},
        401: {"model": ErrorResponse, "description": "Authentication credentials are invalid."},
        403: {"model": ErrorResponse, "description": "The caller or target user lacks required workspace/project membership or permission."},
        404: {"model": ErrorResponse, "description": "Project or target user is missing, archived, or inaccessible."},
        409: {"model": ErrorResponse, "description": "The target user is already a project member."},
    },
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
    summary="List project members",
    description="Requires workspace and project membership; project OWNER and ADMIN can manage members, and every project role can view them.",
    responses={
        401: {"model": ErrorResponse, "description": "Authentication credentials are invalid."},
        403: {"model": ErrorResponse, "description": "Workspace or project membership is missing, or viewing is not permitted."},
        404: {"model": ErrorResponse, "description": "Project is missing, archived, or inaccessible."},
    },
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
    summary="Change a project member's role",
    description="Requires project OWNER or ADMIN role. The existing project OWNER cannot be changed and a second OWNER cannot be created.",
    responses={
        400: {"model": ErrorResponse, "description": "A second project OWNER cannot be created."},
        401: {"model": ErrorResponse, "description": "Authentication credentials are invalid."},
        403: {"model": ErrorResponse, "description": "Workspace/project membership or role-change permission is missing; the OWNER role cannot be changed."},
        404: {"model": ErrorResponse, "description": "Project or target project member is missing, archived, or inaccessible."},
    },
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
    response_model=MessageResponse,
    summary="Remove a project member",
    description="Requires project OWNER or ADMIN role. The project OWNER cannot be removed.",
    responses={
        401: {"model": ErrorResponse, "description": "Authentication credentials are invalid."},
        403: {"model": ErrorResponse, "description": "Workspace/project membership or removal permission is missing, or the target is the project OWNER."},
        404: {"model": ErrorResponse, "description": "Project or target project member is missing, archived, or inaccessible."},
    },
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