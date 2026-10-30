from uuid import uuid4

from app.models.repository import Repository, RepositoryFile, RepositoryStatus, CodeChunk
from app.services.repository_ingestion_service import RepositoryIngestionService


def test_code_chunk_model_relationship_and_transaction_fixture(db_session):
    repository = Repository(project_id=uuid4(), owner="acme", name="demo", url="https://github.com/acme/demo", status=RepositoryStatus.COMPLETED)
    db_session.add(repository)
    db_session.flush()

    file_record = RepositoryFile(repository_id=repository.id, path="main.py", language="python", size_bytes=12, content_hash="a" * 64)
    db_session.add(file_record)
    db_session.flush()
    file_record.chunks.append(CodeChunk(symbol="main", symbol_type="function", parent_symbol=None,
                                        start_line=1, end_line=1, content="def main(): pass",
                                        language="python", chunk_index=0))
    db_session.commit()

    stored = db_session.query(RepositoryFile).filter_by(path="main.py").one()
    assert len(stored.chunks) == 1
    assert stored.chunks[0].symbol == "main"
