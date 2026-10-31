from uuid import UUID

from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session

from app.core.auth import get_current_active_user
from app.core.authorization import require_project_permission
from app.core.permissions import Permission
from app.db.session import get_db
from app.schemas.common import ErrorResponse
from app.schemas.repository import (
    EmbeddingResponse,
    RepositoryConnect,
    RepositoryResponse,
    SemanticSearchRequest,
    SemanticSearchResponse,
)
from app.services.repository_ingestion_service import RepositoryIngestionService
from app.services.embedding_service import EmbeddingService
from app.services.semantic_search_service import SemanticSearchService

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


@router.post(
    "/{project_id}/repositories/{repository_id}/reindex",
    response_model=RepositoryResponse,
    summary="Re-index a connected public GitHub repository",
    description="Requires project:update. Re-clones and atomically replaces repository file and code-chunk metadata.",
    responses={
        401: {"model": ErrorResponse, "description": "Authentication is invalid."},
        403: {"model": ErrorResponse, "description": "The user lacks project:update permission."},
        404: {"model": ErrorResponse, "description": "Project or repository is missing."},
        422: {"model": ErrorResponse, "description": "Repository is unavailable or limits are invalid."},
        502: {"model": ErrorResponse, "description": "Repository clone failed."},
    },
)
def reindex_repository(
    project_id: UUID,
    repository_id: UUID,
    payload: dict = Body(default={}),
    current_user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
    _permission=Depends(require_project_permission(Permission.PROJECT_UPDATE)),
):
    return RepositoryIngestionService(db).reindex_repository(project_id, repository_id)


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


@router.post(
    "/{project_id}/repositories/{repository_id}/embeddings",
    response_model=EmbeddingResponse,
    summary="Generate or retry repository code embeddings",
    description="Requires project:update. Synchronously embeds missing or outdated chunks and never returns source contents or raw vectors.",
    responses={
        401: {"model": ErrorResponse, "description": "Authentication is invalid."},
        403: {"model": ErrorResponse, "description": "The user lacks project:update permission."},
        404: {"model": ErrorResponse, "description": "Project or repository is missing."},
    },
)
def generate_repository_embeddings(
    project_id: UUID,
    repository_id: UUID,
    payload: dict = Body(default={}),
    current_user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
    _permission=Depends(require_project_permission(Permission.PROJECT_UPDATE)),
):
    return EmbeddingService(db).generate_repository_embeddings(project_id, repository_id)


@router.post(
    "/{project_id}/search",
    response_model=SemanticSearchResponse,
    summary="Search project code semantically",
    description="Requires project:view. Searches current-model completed pgvector embeddings with cosine distance and returns project-scoped code snippets.",
    responses={
        401: {"model": ErrorResponse, "description": "Authentication is invalid."},
        403: {"model": ErrorResponse, "description": "The user lacks project:view permission."},
        404: {"model": ErrorResponse, "description": "Project is missing or archived."},
        422: {"model": ErrorResponse, "description": "Search query or limit is invalid."},
        501: {"model": ErrorResponse, "description": "Semantic search requires PostgreSQL with pgvector."},
        502: {"model": ErrorResponse, "description": "Embedding generation failed."},
    },
)
def search_project_code(
    project_id: UUID,
    payload: SemanticSearchRequest,
    current_user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
    _permission=Depends(require_project_permission(Permission.PROJECT_VIEW)),
):
    return SemanticSearchService(db).search(project_id, payload.query, payload.limit)
