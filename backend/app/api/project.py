from uuid import UUID
from typing import Any

from fastapi import APIRouter, Depends  # pyright: ignore[reportMissingImports]

from app.db.session import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
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
    current_user: User = Depends(get_current_active_user),
    db: Any = Depends(get_db),
):
    return ProjectService(db).create_project(
        workspace_id=workspace_id,
        user_id=current_user.id,
        payload=payload,
    )

@router.get(
    "/workspace/{workspace_id}",
    response_model=list[ProjectResponse],
)
def list_projects(
    workspace_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Any = Depends(get_db),
):
    return ProjectService(db).get_projects(
        workspace_id=workspace_id,
        user_id=current_user.id,
    )

@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
)
def get_project(
    project_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Any = Depends(get_db),
):
    return ProjectService(db).get_project(
        project_id=project_id,
        user_id=current_user.id,
    )

@router.patch(
    "/{project_id}",
    response_model=ProjectResponse,
)
def update_project(
    project_id: UUID,
    payload: ProjectUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Any = Depends(get_db),
):
    return ProjectService(db).update_project(
        project_id=project_id,
        user_id=current_user.id,
        payload=payload,
    )

@router.delete("/{project_id}")
def delete_project(
    project_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Any = Depends(get_db),
):
    return ProjectService(db).delete_project(
        project_id=project_id,
        user_id=current_user.id,
    )