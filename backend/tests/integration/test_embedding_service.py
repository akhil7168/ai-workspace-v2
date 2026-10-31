import uuid

from app.models.project import Project
from app.models.repository import CodeChunk, Repository, RepositoryFile, RepositoryStatus
from app.models.user import User
from app.models.workspace import Workspace
from app.services.embedding_service import EmbeddingService


class FakeProvider:
    def __init__(self, model_name="fake/model-v1", fail=False):
        self.model_name = model_name
        self.dimension = 384
        self.fail = fail

    def generate(self, texts):
        if self.fail:
            raise RuntimeError("provider failure")
        return [[1.0 / (384 ** 0.5)] * 384 for _ in texts]


def create_repository_graph(db_session):
    user = User(
        id=uuid.uuid4(),
        full_name="Embedding User",
        email=f"embedding-{uuid.uuid4()}@example.com",
        password_hash="not-used",
        role="user",
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    workspace = Workspace(
        id=uuid.uuid4(),
        owner_id=user.id,
        name="Embedding Workspace",
        is_archived=False,
    )
    db_session.add(workspace)
    project = Project(
        id=uuid.uuid4(),
        workspace_id=workspace.id,
        created_by=user.id,
        title="Embedding Project",
        status="ACTIVE",
    )
    db_session.add(project)
    repository = Repository(
        id=uuid.uuid4(),
        project_id=project.id,
        owner="acme",
        name="embedding",
        url="https://github.com/acme/embedding",
        status=RepositoryStatus.COMPLETED,
    )
    db_session.add(repository)
    db_session.flush()
    file_record = RepositoryFile(
        id=uuid.uuid4(),
        repository_id=repository.id,
        path="main.py",
        language="python",
        size_bytes=20,
        content_hash="a" * 64,
    )
    db_session.add(file_record)
    db_session.flush()
    chunk = CodeChunk(
        id=uuid.uuid4(),
        file_id=file_record.id,
        symbol="main",
        symbol_type="function",
        start_line=1,
        end_line=2,
        content="def main():\n    pass",
        language="python",
        chunk_index=0,
    )
    db_session.add(chunk)
    db_session.commit()
    return project, repository, chunk


def test_embedding_service_is_idempotent_model_versioned_and_retryable(db_session):
    project, repository, chunk = create_repository_graph(db_session)

    first = EmbeddingService(db_session, provider=FakeProvider(), batch_size=1).generate_repository_embeddings(
        project.id, repository.id
    )
    assert first["newly_embedded"] == 1
    assert first["failed"] == 0
    db_session.refresh(chunk)
    assert chunk.embedding_status == "COMPLETED"
    assert chunk.embedding_model == "fake/model-v1"
    assert chunk.embedding is not None

    second = EmbeddingService(db_session, provider=FakeProvider(), batch_size=1).generate_repository_embeddings(
        project.id, repository.id
    )
    assert second["newly_embedded"] == 0
    assert second["already_embedded"] == 1

    changed = EmbeddingService(
        db_session, provider=FakeProvider(model_name="fake/model-v2"), batch_size=1
    ).generate_repository_embeddings(project.id, repository.id)
    assert changed["newly_embedded"] == 1
    db_session.refresh(chunk)
    assert chunk.embedding_model == "fake/model-v2"

    failed = EmbeddingService(
        db_session, provider=FakeProvider(model_name="fake/model-v3", fail=True), batch_size=1
    ).generate_repository_embeddings(project.id, repository.id)
    assert failed["failed"] == 1
    db_session.refresh(chunk)
    assert chunk.embedding is None
    assert chunk.embedding_status == "FAILED"

    retried = EmbeddingService(
        db_session, provider=FakeProvider(model_name="fake/model-v3"), batch_size=1
    ).generate_repository_embeddings(project.id, repository.id)
    assert retried["newly_embedded"] == 1
    db_session.refresh(chunk)
    assert chunk.embedding_status == "COMPLETED"
