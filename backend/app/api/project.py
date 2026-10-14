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
from app.services.project_service import ProjectService


router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)


@router.post(
    "/workspace/{workspace_id}",
    response_model=ProjectResponse,
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