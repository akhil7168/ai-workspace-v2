import os
from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.project import ProjectStatus
from app.models.repository import Repository, RepositoryFile, RepositoryStatus, CodeChunk
from app.ingestion.scanner import IngestionSourceScanner
from app.ingestion.parser import parse_source
from app.ingestion.chunker import generate_chunks
from app.repositories.repository_repository import RepositoryRepository
from app.services.project_service import ProjectService
from app.utils.repository_ingestion import (
    GitHubCloneAdapter,
    RepositoryCloneError,
    RepositoryFileScanner,
    RepositoryLimitError,
    RepositoryValidationError,
    GitHubPublicRepositoryVerifier,
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
        self.public_verifier = GitHubPublicRepositoryVerifier(settings.REPOSITORY_CLONE_TIMEOUT_SECONDS)
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

    def _build_indexed_snapshot(self, url: str):
        clone_root = None
        try:
            clone_root = create_temporary_clone_directory()
            checkout_root = os.path.join(clone_root, "checkout")
            snapshot = self.clone_adapter.clone(url, checkout_root)
            metadata = self.scanner.scan(checkout_root)
            source_files = IngestionSourceScanner().read_files(
                checkout_root, metadata, settings.REPOSITORY_MAX_FILE_BYTES
            )
            source_by_path = {item.relative_path: item for item in source_files}
            replacement_files: list[RepositoryFile] = []
            fallback_file_count = 0
            for item in metadata:
                file_record = RepositoryFile(
                    path=item.path,
                    language=item.language,
                    size_bytes=item.size_bytes,
                    content_hash=item.content_hash,
                )
                source_file = source_by_path.get(item.path)
                if source_file is None:
                    replacement_files.append(file_record)
                    continue
                parsed = parse_source(source_file.content, source_file.language, source_file.relative_path)
                candidates = generate_chunks(
                    source_file.content,
                    source_file.language,
                    parsed,
                    settings.CODE_CHUNK_MAX_CHARS,
                )
                if not parsed and source_file.language in {"python", "javascript", "jsx", "typescript", "tsx", "java"}:
                    fallback_file_count += 1
                for candidate in candidates:
                    file_record.chunks.append(CodeChunk(
                        symbol=candidate.symbol,
                        symbol_type=candidate.symbol_type,
                        parent_symbol=candidate.parent_symbol,
                        start_line=candidate.start_line,
                        end_line=candidate.end_line,
                        content=candidate.content,
                        language=candidate.language,
                        chunk_index=candidate.chunk_index,
                    ))
                replacement_files.append(file_record)
            return snapshot, metadata, replacement_files, fallback_file_count
        finally:
            cleanup_temporary_directory(clone_root)

    def reindex_repository(self, project_id: UUID, repository_id: UUID):
        project = ProjectService(self.db).get_project(project_id)
        if project.status == ProjectStatus.ARCHIVED or not project.workspace or project.workspace.is_archived:
            raise HTTPException(status_code=404, detail="Project not found")
        repository = self.repo.get_by_project_and_id(project_id, repository_id)
        if repository is None:
            raise HTTPException(status_code=404, detail="Repository not found")

        try:
            normalized, owner, name = validate_github_url(repository.url)
            self.public_verifier.verify(owner, name)
        except RepositoryValidationError as exc:
            repository.status = RepositoryStatus.FAILED
            repository.error_message = str(exc)
            self.db.commit()
            raise HTTPException(status_code=422, detail=str(exc)) from exc

        try:
            snapshot, metadata, replacement_files, fallback_file_count = self._build_indexed_snapshot(normalized)
        except RepositoryLimitError as exc:
            repository.status = RepositoryStatus.FAILED
            repository.error_message = str(exc)
            self.db.commit()
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except RepositoryCloneError as exc:
            repository.status = RepositoryStatus.FAILED
            repository.error_message = str(exc)
            self.db.commit()
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        except Exception:
            repository.status = RepositoryStatus.FAILED
            repository.error_message = "Repository ingestion failed"
            self.db.commit()
            raise HTTPException(status_code=500, detail="Repository ingestion failed")

        try:
            repository.files.clear()
            for file_record in replacement_files:
                repository.files.append(file_record)
            repository.status = RepositoryStatus.COMPLETED
            repository.branch = snapshot.branch
            repository.commit_sha = snapshot.commit_sha
            repository.file_count = len(metadata)
            repository.total_size_bytes = sum(item.size_bytes for item in metadata)
            repository.error_message = f"Fallback parsing used for {fallback_file_count} file(s)" if fallback_file_count else None
            repository.indexed_at = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(repository)
            return repository
        except Exception:
            self.db.rollback()
            repository.status = RepositoryStatus.FAILED
            repository.error_message = "Repository ingestion failed while replacing indexed data"
            self.db.commit()
            raise HTTPException(status_code=500, detail="Repository re-index failed")

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
        try:
            self.public_verifier.verify(owner, name)
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

            source_files = IngestionSourceScanner().read_files(
                checkout_root, metadata, settings.REPOSITORY_MAX_FILE_BYTES
            )

            repository.status = RepositoryStatus.COMPLETED
            repository.branch = snapshot.branch
            repository.commit_sha = snapshot.commit_sha
            repository.file_count = len(metadata)
            repository.total_size_bytes = sum(item.size_bytes for item in metadata)
            repository.error_message = None
            repository.indexed_at = datetime.now(timezone.utc)
            repository.files.clear()

            source_by_path = {item.relative_path: item for item in source_files}
            fallback_file_count = 0
            unexpected_parser_error = False
            for item in metadata:
                file_record = RepositoryFile(
                    path=item.path,
                    language=item.language,
                    size_bytes=item.size_bytes,
                    content_hash=item.content_hash,
                )
                repository.files.append(file_record)
                source_file = source_by_path.get(item.path)
                if source_file is None:
                    continue
                try:
                    parsed = parse_source(source_file.content, source_file.language, source_file.relative_path)
                    candidates = generate_chunks(
                        source_file.content,
                        source_file.language,
                        parsed,
                        settings.CODE_CHUNK_MAX_CHARS,
                    )
                    if not parsed and source_file.language in {"python", "javascript", "jsx", "typescript", "tsx", "java"}:
                        fallback_file_count += 1
                    for candidate in candidates:
                        file_record.chunks.append(CodeChunk(
                            symbol=candidate.symbol,
                            symbol_type=candidate.symbol_type,
                            parent_symbol=candidate.parent_symbol,
                            start_line=candidate.start_line,
                            end_line=candidate.end_line,
                            content=candidate.content,
                            language=candidate.language,
                            chunk_index=candidate.chunk_index,
                        ))
                except Exception:
                    unexpected_parser_error = True
                    break

            if unexpected_parser_error:
                repository.status = RepositoryStatus.FAILED
                repository.error_message = "A parsing error prevented complete indexing"
                repository.file_count = 0
                repository.total_size_bytes = 0
                repository.files.clear()
                repository.indexed_at = None
                self.db.commit()
                raise HTTPException(status_code=500, detail="Repository ingestion failed")

            if fallback_file_count:
                repository.error_message = f"Fallback parsing used for {fallback_file_count} file(s)"
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
