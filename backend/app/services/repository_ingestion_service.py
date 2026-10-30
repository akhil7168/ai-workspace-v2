import os
from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.project import ProjectStatus
from app.models.repository import Repository, RepositoryFile, RepositoryStatus
from app.repositories.repository_repository import RepositoryRepository
from app.services.project_service import ProjectService
from app.utils.repository_ingestion import (
    GitHubCloneAdapter,
    RepositoryCloneError,
    RepositoryFileScanner,
    RepositoryLimitError,
    RepositoryValidationError,
    cleanup_temporary_directory,
    create_temporary_clone_directory,
    validate_github_url,
)


class RepositoryIngestionService:
    def __init__(self, db: Session, clone_adapter: GitHubCloneAdapter | None = None,
                 scanner: RepositoryFileScanner | None = None):
        self.db = db
        self.repo = RepositoryRepository(db)
        self.clone_adapter = clone_adapter or GitHubCloneAdapter(settings.REPOSITORY_CLONE_TIMEOUT_SECONDS)
        self.scanner = scanner or RepositoryFileScanner(
            max_file_bytes=settings.REPOSITORY_MAX_FILE_BYTES,
            max_files=settings.REPOSITORY_MAX_FILES,
            max_total_bytes=settings.REPOSITORY_MAX_TOTAL_BYTES,
            max_processing_seconds=settings.REPOSITORY_MAX_PROCESSING_SECONDS,
        )

    def list_repositories(self, project_id: UUID):
        project = ProjectService(self.db).get_project(project_id)
        if not project.workspace or project.workspace.is_archived:
            raise HTTPException(status_code=404, detail="Project not found")
        return self.repo.list_by_project(project_id)

    def connect_repository(self, project_id: UUID, url: str):
        project = ProjectService(self.db).get_project(project_id)
        if project.status == ProjectStatus.ARCHIVED:
            raise HTTPException(status_code=404, detail="Project not found")
        if project.workspace is None or project.workspace.is_archived:
            raise HTTPException(status_code=404, detail="Project not found")

        try:
            normalized, owner, name = validate_github_url(url)
        except RepositoryValidationError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

        existing = self.repo.get_by_project_and_url(project_id, normalized)
        if existing:
            raise HTTPException(status_code=409, detail="Repository is already connected to this project")

        repository = Repository(
            project_id=project_id,
            owner=owner,
            name=name,
            url=normalized,
            status=RepositoryStatus.PENDING,
        )
        self.db.add(repository)
        self.db.commit()
        self.db.refresh(repository)

        clone_root = None
        try:
            clone_root = create_temporary_clone_directory()
            checkout_root = os.path.join(clone_root, "checkout")
            snapshot = self.clone_adapter.clone(normalized, checkout_root)
            metadata = self.scanner.scan(checkout_root)

            repository.status = RepositoryStatus.COMPLETED
            repository.branch = snapshot.branch
            repository.commit_sha = snapshot.commit_sha
            repository.file_count = len(metadata)
            repository.total_size_bytes = sum(item.size_bytes for item in metadata)
            repository.error_message = None
            repository.indexed_at = datetime.now(timezone.utc)
            repository.files.clear()
            for item in metadata:
                repository.files.append(RepositoryFile(
                    path=item.path,
                    language=item.language,
                    size_bytes=item.size_bytes,
                    content_hash=item.content_hash,
                ))
            self.db.commit()
            self.db.refresh(repository)
            return repository
        except RepositoryLimitError as exc:
            repository.status = RepositoryStatus.FAILED
            repository.error_message = str(exc)
            repository.file_count = 0
            repository.total_size_bytes = 0
            self.db.commit()
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except RepositoryCloneError as exc:
            repository.status = RepositoryStatus.FAILED
            repository.error_message = str(exc)
            repository.file_count = 0
            repository.total_size_bytes = 0
            self.db.commit()
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        except Exception:
            repository.status = RepositoryStatus.FAILED
            repository.error_message = "Repository ingestion failed"
            repository.file_count = 0
            repository.total_size_bytes = 0
            self.db.commit()
            raise HTTPException(status_code=500, detail="Repository ingestion failed")
        finally:
            cleanup_temporary_directory(clone_root)
