from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import get_current_active_user
from app.core.authorization import require_project_permission
from app.core.permissions import Permission
from app.db.session import get_db
from app.schemas.common import ErrorResponse
from app.schemas.repository import RepositoryConnect, RepositoryResponse
from app.services.repository_ingestion_service import RepositoryIngestionService

router = APIRouter(prefix="/projects", tags=["Repositories"])


@router.post(
    "/{project_id}/repositories",
    response_model=RepositoryResponse,
    summary="Connect and ingest a public GitHub repository",
    description="Requires project:update. Validates a public github.com HTTPS URL, performs a shallow clone, scans eligible text files, and stores repository/file metadata without source contents.",
    responses={
        401: {"model": ErrorResponse, "description": "Authentication is invalid."},
        403: {"model": ErrorResponse, "description": "The user lacks project:update permission."},
        404: {"model": ErrorResponse, "description": "Project is missing or archived."},
        409: {"model": ErrorResponse, "description": "Repository is already connected."},
        422: {"model": ErrorResponse, "description": "URL or ingestion limits are invalid."},
        502: {"model": ErrorResponse, "description": "Repository clone failed."},
    },
)
def connect_repository(
    project_id: UUID,
    payload: RepositoryConnect,
    current_user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
    _permission=Depends(require_project_permission(Permission.PROJECT_UPDATE)),
):
    return RepositoryIngestionService(db).connect_repository(project_id, payload.url)


@router.get(
    "/{project_id}/repositories",
    response_model=list[RepositoryResponse],
    summary="List repositories connected to a project",
    description="Requires project:view and returns project-scoped repository metadata only.",
    responses={
        401: {"model": ErrorResponse, "description": "Authentication is invalid."},
        403: {"model": ErrorResponse, "description": "The user lacks project:view permission."},
        404: {"model": ErrorResponse, "description": "Project is missing or archived."},
    },
)
def list_repositories(
    project_id: UUID,
    current_user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
    _permission=Depends(require_project_permission(Permission.PROJECT_VIEW)),
):
    return RepositoryIngestionService(db).list_repositories(project_id)
