from datetime import datetime, timezone
import logging
import math
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.authorization import require_project_permission
from app.embeddings.sentence_transformer_provider import SentenceTransformerEmbeddingProvider
from app.models.project import ProjectStatus
from app.models.repository import CodeChunk, RepositoryFile, Repository
from app.services.project_service import ProjectService
from app.repositories.repository_repository import RepositoryRepository

logger = logging.getLogger(__name__)


class EmbeddingService:
    def __init__(self, db: Session, provider=None, batch_size: int | None = None):
        self.db = db
        self.provider = provider or SentenceTransformerEmbeddingProvider(
            model_name=settings.EMBEDDING_MODEL_NAME,
            dimension=settings.EMBEDDING_DIMENSION,
            device=settings.EMBEDDING_DEVICE,
        )
        self.batch_size = batch_size or settings.EMBEDDING_BATCH_SIZE
        if self.batch_size < 1:
            raise ValueError("Embedding batch size must be at least 1")
        self.model_name = self.provider.model_name
        self.dimension = getattr(self.provider, "dimension", settings.EMBEDDING_DIMENSION)

    def _repository_chunks_query(self, repository_id: UUID):
        return (
            self.db.query(CodeChunk)
            .join(RepositoryFile, CodeChunk.file_id == RepositoryFile.id)
            .filter(RepositoryFile.repository_id == repository_id)
        )

    def generate_repository_embeddings(self, project_id: UUID, repository_id: UUID) -> dict:
        project = ProjectService(self.db).get_project(project_id)
        if project.status == ProjectStatus.ARCHIVED or not project.workspace or project.workspace.is_archived:
            raise HTTPException(status_code=404, detail="Project not found")
        repository = RepositoryRepository(self.db).get_by_project_and_id(project_id, repository_id)
        if repository is None:
            raise HTTPException(status_code=404, detail="Repository not found")

        total = self._repository_chunks_query(repository_id).count()
        already_embedded = self._repository_chunks_query(repository_id).filter(
            CodeChunk.embedding.is_not(None),
            CodeChunk.embedding_status == "COMPLETED",
            CodeChunk.embedding_model == self.model_name,
        ).count()

        newly_embedded = 0
        failed = 0
        processed_ids = []
        while True:
            candidates = (
                self._repository_chunks_query(repository_id)
                .filter(or_(
                    CodeChunk.embedding.is_(None),
                    CodeChunk.embedding_status.is_(None),
                    CodeChunk.embedding_status != "COMPLETED",
                    CodeChunk.embedding_model.is_(None),
                    CodeChunk.embedding_model != self.model_name,
                ))
            )
            if processed_ids:
                candidates = candidates.filter(CodeChunk.id.notin_(processed_ids))
            candidates = (
                candidates
                .order_by(CodeChunk.created_at, CodeChunk.chunk_index)
                .limit(self.batch_size)
                .all()
            )
            if not candidates:
                break
            processed_ids.extend(chunk.id for chunk in candidates)

            try:
                vectors = self.provider.generate([chunk.content for chunk in candidates])
                if len(vectors) != len(candidates):
                    raise ValueError(
                        f"Embedding provider returned {len(vectors)} vectors for {len(candidates)} chunks"
                    )
                now = datetime.now(timezone.utc)
                for chunk, vector in zip(candidates, vectors):
                    if len(vector) != self.dimension:
                        raise ValueError(
                            f"Embedding dimension must be {self.dimension}"
                        )
                    if any(not isinstance(value, (int, float)) or not math.isfinite(float(value)) for value in vector):
                        raise ValueError("Embedding output contains NaN or infinite values")
                    chunk.embedding = vector
                    chunk.embedding_model = self.model_name
                    chunk.embedding_status = "COMPLETED"
                    chunk.embedded_at = now
                    newly_embedded += 1
                self.db.commit()
            except Exception:
                logger.exception(
                    "Embedding batch failed for repository %s; marking %s chunks FAILED",
                    repository_id,
                    len(candidates),
                )
                now = datetime.now(timezone.utc)
                for chunk in candidates:
                    chunk.embedding = None
                    chunk.embedding_status = "FAILED"
                    chunk.embedding_model = self.model_name
                    chunk.embedded_at = now
                    failed += 1
                self.db.commit()

        current_failed = self._repository_chunks_query(repository_id).filter(
            CodeChunk.embedding_status == "FAILED"
        ).count()
        failed = max(failed, current_failed)
        return {
            "total_chunks": total,
            "already_embedded": already_embedded,
            "newly_embedded": newly_embedded,
            "failed": failed,
            "model_name": self.model_name,
        }
