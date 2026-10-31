import math
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import bindparam, Float, type_coerce
from sqlalchemy.orm import Session

from app.core.config import settings
from app.embeddings.sentence_transformer_provider import SentenceTransformerEmbeddingProvider
from app.models.repository import CodeChunk, Repository, RepositoryFile
from app.services.project_service import ProjectService


class SemanticSearchService:
    SNIPPET_MAX_CHARS = 2000

    def __init__(self, db: Session, provider=None):
        self.db = db
        self.provider = provider or SentenceTransformerEmbeddingProvider(
            model_name=settings.EMBEDDING_MODEL_NAME,
            dimension=settings.EMBEDDING_DIMENSION,
            device=settings.EMBEDDING_DEVICE,
        )
        self.model_name = self.provider.model_name
        self.dimension = getattr(self.provider, "dimension", settings.EMBEDDING_DIMENSION)

    def search(self, project_id: UUID, query: str, limit: int = 5) -> dict:
        ProjectService(self.db).get_project(project_id)
        if self.db.get_bind().dialect.name != "postgresql":
            raise HTTPException(
                status_code=501,
                detail="Semantic search requires PostgreSQL with pgvector",
            )

        if limit < 1 or limit > 20:
            raise HTTPException(status_code=422, detail="Limit must be between 1 and 20")
        if not isinstance(query, str) or not query.strip():
            raise HTTPException(status_code=422, detail="Query must not be empty")

        try:
            vectors = self.provider.generate([query.strip()])
        except Exception as exc:
            raise HTTPException(
                status_code=502,
                detail="Embedding generation failed",
            ) from exc

        if len(vectors) != 1:
            raise HTTPException(status_code=502, detail="Embedding generation failed")
        query_vector = vectors[0]
        if (
            len(query_vector) != self.dimension
            or any(
                not isinstance(value, (int, float)) or not math.isfinite(float(value))
                for value in query_vector
            )
        ):
            raise HTTPException(status_code=502, detail="Embedding generation failed")

        from pgvector.sqlalchemy import Vector

        query_embedding = bindparam(
            "query_embedding",
            value=query_vector,
            type_=Vector(self.dimension),
        )
        distance = type_coerce(
            CodeChunk.embedding.op("<=>")(query_embedding),
            Float(),
        )

        rows = (
            self.db.query(
                CodeChunk.id.label("chunk_id"),
                Repository.id.label("repository_id"),
                RepositoryFile.path.label("file_path"),
                CodeChunk.symbol.label("symbol"),
                CodeChunk.symbol_type.label("symbol_type"),
                CodeChunk.start_line.label("start_line"),
                CodeChunk.end_line.label("end_line"),
                CodeChunk.language.label("language"),
                CodeChunk.content.label("content"),
                distance.label("distance"),
            )
            .select_from(CodeChunk)
            .join(RepositoryFile, CodeChunk.file_id == RepositoryFile.id)
            .join(Repository, RepositoryFile.repository_id == Repository.id)
            .filter(
                Repository.project_id == project_id,
                CodeChunk.embedding.is_not(None),
                CodeChunk.embedding_status == "COMPLETED",
                CodeChunk.embedding_model == self.model_name,
            )
            .order_by(distance.asc())
            .limit(limit)
            .all()
        )

        results = []
        for row in rows:
            similarity = max(-1.0, min(1.0, 1.0 - float(row.distance)))
            content = row.content or ""
            snippet = content[: self.SNIPPET_MAX_CHARS]
            results.append({
                "chunk_id": row.chunk_id,
                "repository_id": row.repository_id,
                "file_path": row.file_path,
                "symbol": row.symbol,
                "symbol_type": row.symbol_type,
                "start_line": row.start_line,
                "end_line": row.end_line,
                "language": row.language,
                "similarity": similarity,
                "snippet": snippet,
            })

        return {
            "query": query.strip(),
            "model_name": self.model_name,
            "total": len(results),
            "results": results,
        }
