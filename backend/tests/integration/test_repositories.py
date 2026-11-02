import os
from uuid import UUID

import pytest
from fastapi import HTTPException

from app.core.config import settings
from app.llm.provider import OpenAICompatibleLLMProvider
from app.models.repository import Repository, RepositoryFile, RepositoryStatus, CodeChunk
from app.services.rag_service import RAGService
from app.services.semantic_search_service import SemanticSearchService
from app.utils.repository_ingestion import GitSnapshot, FileMetadata, GitHubCloneAdapter, GitHubPublicRepositoryVerifier, RepositoryCloneError, RepositoryFileScanner


def create_workspace_project(client, account, title="Repository project"):
    workspace = client.post("/workspaces", headers=account["headers"], json={"name": "Repository workspace"})
    assert workspace.status_code == 200, workspace.text
    project = client.post(f"/projects/workspace/{workspace.json()['id']}", headers=account["headers"], json={"title": title})
    assert project.status_code == 200, project.text
    return workspace.json(), project.json()


def test_ingest_and_list_repository(monkeypatch, client, db_session, authenticated_user):
    monkeypatch.setattr(GitHubPublicRepositoryVerifier, "verify", lambda self, owner, name: None)
    owner = authenticated_user()
    _, project = create_workspace_project(client, owner)

    monkeypatch.setattr(GitHubCloneAdapter, "clone", lambda self, url, destination: GitSnapshot(destination, "0123456789abcdef0123456789abcdef01234567", "main"))
    monkeypatch.setattr(RepositoryFileScanner, "scan", lambda self, root: [
        FileMetadata("src/app.py", "python", 12, "a" * 64),
        FileMetadata("README.md", "markdown", 20, "b" * 64),
    ])

    response = client.post(
        f"/projects/{project['id']}/repositories",
        headers=owner["headers"],
        json={"url": "https://github.com/acme/widget.git"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["url"] == "https://github.com/acme/widget"
    assert body["status"] == "COMPLETED"
    assert body["commit_sha"] == "0123456789abcdef0123456789abcdef01234567"
    assert body["file_count"] == 2

    listed = client.get(f"/projects/{project['id']}/repositories", headers=owner["headers"])
    assert listed.status_code == 200
    assert listed.json()[0]["id"] == body["id"]

    duplicate = client.post(
        f"/projects/{project['id']}/repositories",
        headers=owner["headers"],
        json={"url": "https://github.com/acme/widget"},
    )
    assert duplicate.status_code == 409


def test_ingestion_persists_python_chunks(monkeypatch, client, db_session, authenticated_user):
    monkeypatch.setattr(GitHubPublicRepositoryVerifier, "verify", lambda self, owner, name: None)
    owner = authenticated_user()
    _, project = create_workspace_project(client, owner)

    def clone_fixture(self, url, destination):
        os.makedirs(destination, exist_ok=True)
        with open(os.path.join(destination, "main.py"), "w", encoding="utf-8", newline="") as handle:
            handle.write("def hello():\n    return 'world'\n")
        return GitSnapshot(destination, "0123456789abcdef0123456789abcdef01234567", "main")

    monkeypatch.setattr(GitHubCloneAdapter, "clone", clone_fixture)
    monkeypatch.setattr(RepositoryFileScanner, "scan", lambda self, root: [
        FileMetadata("main.py", "python", 32, "c" * 64),
    ])

    response = client.post(
        f"/projects/{project['id']}/repositories",
        headers=owner["headers"],
        json={"url": "https://github.com/acme/chunks"},
    )
    assert response.status_code == 200, response.text
    repository = db_session.query(Repository).filter_by(url="https://github.com/acme/chunks").one()
    assert repository.status == RepositoryStatus.COMPLETED
    assert len(repository.files) == 1
    assert len(repository.files[0].chunks) == 1
    chunk = repository.files[0].chunks[0]
    assert chunk.symbol == "hello"
    assert chunk.start_line == 1
    assert chunk.end_line == 2
    assert chunk.content == "def hello():\n    return 'world'\n"


def test_reindex_replaces_stale_files_and_chunks(monkeypatch, client, db_session, authenticated_user):
    monkeypatch.setattr(GitHubPublicRepositoryVerifier, "verify", lambda self, owner, name: None)
    owner = authenticated_user()
    _, project = create_workspace_project(client, owner, "Reindex project")
    repository = Repository(
        project_id=UUID(project["id"]), owner="acme", name="reindex", url="https://github.com/acme/reindex",
        status=RepositoryStatus.COMPLETED, commit_sha="old", file_count=1,
    )
    db_session.add(repository)
    db_session.flush()
    old_file = RepositoryFile(repository_id=repository.id, path="old.py", language="python", size_bytes=3, content_hash="d" * 64)
    old_file.chunks.append(CodeChunk(symbol="old", symbol_type="function", parent_symbol=None,
                                     start_line=1, end_line=1, content="old", language="python", chunk_index=0))
    repository.files.append(old_file)
    db_session.commit()

    def clone_fixture(self, url, destination):
        os.makedirs(destination, exist_ok=True)
        with open(os.path.join(destination, "new.py"), "w", encoding="utf-8", newline="") as handle:
            handle.write("def new():\r\n    return 2\r\n")
        return GitSnapshot(destination, "b" * 40, "main")

    monkeypatch.setattr(GitHubCloneAdapter, "clone", clone_fixture)
    monkeypatch.setattr(RepositoryFileScanner, "scan", lambda self, root: [
        FileMetadata("new.py", "python", 25, "e" * 64),
    ])

    response = client.post(
        f"/projects/{project['id']}/repositories/{repository.id}/reindex",
        headers=owner["headers"],
    )
    assert response.status_code == 200, response.text
    db_session.expire_all()
    stored = db_session.query(Repository).filter_by(id=repository.id).one()
    assert stored.status == RepositoryStatus.COMPLETED
    assert [file.path for file in stored.files] == ["new.py"]
    assert len(stored.files[0].chunks) == 1
    assert stored.files[0].chunks[0].symbol == "new"
    assert stored.files[0].chunks[0].content == "def new():\r\n    return 2\r\n"


def test_reindex_failure_preserves_previous_successful_data(monkeypatch, client, db_session, authenticated_user):
    monkeypatch.setattr(GitHubPublicRepositoryVerifier, "verify", lambda self, owner, name: None)
    owner = authenticated_user()
    _, project = create_workspace_project(client, owner, "Failed reindex project")
    repository = Repository(
        project_id=UUID(project["id"]), owner="acme", name="keep", url="https://github.com/acme/keep",
        status=RepositoryStatus.COMPLETED, commit_sha="old", file_count=1,
    )
    db_session.add(repository)
    db_session.flush()
    old_file = RepositoryFile(repository_id=repository.id, path="keep.py", language="python", size_bytes=8, content_hash="f" * 64)
    old_file.chunks.append(CodeChunk(symbol="keep", symbol_type="function", parent_symbol=None,
                                     start_line=1, end_line=1, content="def keep():", language="python", chunk_index=0))
    repository.files.append(old_file)
    db_session.commit()

    def clone_failure(self, url, destination):
        raise RepositoryCloneError("Repository clone failed")

    monkeypatch.setattr(GitHubCloneAdapter, "clone", clone_failure)
    response = client.post(
        f"/projects/{project['id']}/repositories/{repository.id}/reindex",
        headers=owner["headers"],
    )
    assert response.status_code == 502
    db_session.expire_all()
    stored = db_session.query(Repository).filter_by(id=repository.id).one()
    assert stored.status == RepositoryStatus.FAILED
    assert [file.path for file in stored.files] == ["keep.py"]
    assert stored.files[0].chunks[0].content == "def keep():"


def test_repository_route_authorization(monkeypatch, client, authenticated_user):
    owner = authenticated_user()
    workspace, project = create_workspace_project(client, owner)
    viewer = authenticated_user()
    added = client.post(
        f"/memberships/{workspace['id']}",
        headers=owner["headers"],
        json={"user_id": viewer["user"]["id"], "role": "VIEWER"},
    )
    assert added.status_code == 201

    denied = client.post(
        f"/projects/{project['id']}/repositories",
        headers=viewer["headers"],
        json={"url": "https://github.com/acme/widget"},
    )
    assert denied.status_code == 403
    denied_reindex = client.post(
        f"/projects/{project['id']}/repositories/{UUID(int=0)}/reindex",
        headers=viewer["headers"],
    )
    assert denied_reindex.status_code == 403
    listed = client.get(f"/projects/{project['id']}/repositories", headers=viewer["headers"])
    assert listed.status_code == 200


def test_semantic_search_route_requires_pgvector(client, authenticated_user):
    owner = authenticated_user()
    _, project = create_workspace_project(client, owner, "Search project")

    response = client.post(
        f"/projects/{project['id']}/search",
        headers=owner["headers"],
        json={"query": "find the authentication handler", "limit": 3},
    )
    assert response.status_code == 501
    assert "PostgreSQL with pgvector" in response.json()["detail"]


def test_semantic_search_route_validates_query_and_limit(client, authenticated_user):
    owner = authenticated_user()
    _, project = create_workspace_project(client, owner, "Search validation project")

    empty = client.post(
        f"/projects/{project['id']}/search",
        headers=owner["headers"],
        json={"query": "   ", "limit": 5},
    )
    assert empty.status_code == 422

    excessive_limit = client.post(
        f"/projects/{project['id']}/search",
        headers=owner["headers"],
        json={"query": "authentication", "limit": 21},
    )
    assert excessive_limit.status_code == 422


def test_semantic_search_route_allows_project_viewer(client, authenticated_user):
    owner = authenticated_user()
    workspace, project = create_workspace_project(client, owner, "Viewer search project")
    viewer = authenticated_user()
    added = client.post(
        f"/memberships/{workspace['id']}",
        headers=owner["headers"],
        json={"user_id": viewer["user"]["id"], "role": "VIEWER"},
    )
    assert added.status_code == 201

    response = client.post(
        f"/projects/{project['id']}/search",
        headers=viewer["headers"],
        json={"query": "authentication", "limit": 5},
    )
    assert response.status_code == 501
    assert "PostgreSQL with pgvector" in response.json()["detail"]


def test_semantic_search_route_denies_workspace_non_member(client, authenticated_user):
    owner = authenticated_user()
    _, project = create_workspace_project(client, owner, "Private search project")
    outsider = authenticated_user()

    response = client.post(
        f"/projects/{project['id']}/search",
        headers=outsider["headers"],
        json={"query": "authentication", "limit": 5},
    )
    assert response.status_code == 403


def test_rag_route_validates_question_and_limit(client, authenticated_user):
    owner = authenticated_user()
    _, project = create_workspace_project(client, owner, "RAG validation project")

    empty = client.post(
        f"/projects/{project['id']}/ask",
        headers=owner["headers"],
        json={"question": "   ", "limit": 5},
    )
    assert empty.status_code == 422

    excessive_limit = client.post(
        f"/projects/{project['id']}/ask",
        headers=owner["headers"],
        json={"question": "authentication", "limit": 21},
    )
    assert excessive_limit.status_code == 422

    oversized = client.post(
        f"/projects/{project['id']}/ask",
        headers=owner["headers"],
        json={"question": "x" * 4001, "limit": 5},
    )
    assert oversized.status_code == 422


def test_rag_route_requires_pgvector(client, authenticated_user):
    owner = authenticated_user()
    _, project = create_workspace_project(client, owner, "RAG search project")

    response = client.post(
        f"/projects/{project['id']}/ask",
        headers=owner["headers"],
        json={"question": "Where is authentication implemented?", "limit": 3},
    )
    assert response.status_code == 501
    assert "PostgreSQL with pgvector" in response.json()["detail"]


def test_rag_route_denies_workspace_non_member(client, authenticated_user):
    owner = authenticated_user()
    _, project = create_workspace_project(client, owner, "Private RAG project")
    outsider = authenticated_user()

    response = client.post(
        f"/projects/{project['id']}/ask",
        headers=outsider["headers"],
        json={"question": "authentication", "limit": 5},
    )
    assert response.status_code == 403


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"message": ""},
        {"message": "   "},
        {"message": "x" * 4001},
        [],
    ],
)
def test_assistant_chat_schema_validation(client, authenticated_user, payload):
    owner = authenticated_user()
    _, project = create_workspace_project(client, owner, "Assistant validation project")

    response = client.post(
        f"/projects/{project['id']}/assistant/chat",
        headers=owner["headers"],
        json=payload,
    )
    assert response.status_code == 422


def test_assistant_chat_requires_authentication(client, authenticated_user):
    owner = authenticated_user()
    _, project = create_workspace_project(client, owner, "Assistant auth project")

    response = client.post(
        f"/projects/{project['id']}/assistant/chat",
        json={"message": "Explain authentication"},
    )
    assert response.status_code == 401


def test_assistant_chat_valid_owner(monkeypatch, client, authenticated_user):
    owner = authenticated_user()
    _, project = create_workspace_project(client, owner, "Assistant owner project")
    calls = []

    def fake_ask(self, project_id, message, limit):
        calls.append((project_id, message, limit))
        return {
            "answer": "Authentication is handled by auth/service.py [1]",
            "sources": [{
                "file_path": "auth/service.py",
                "start_line": 45,
                "end_line": 93,
                "chunk_id": UUID("11111111-1111-4111-8111-111111111111"),
                "similarity": 0.91,
            }],
            "retrieval_count": 1,
            "model_name": "test-model",
        }

    monkeypatch.setattr(RAGService, "ask", fake_ask)
    response = client.post(
        f"/projects/{project['id']}/assistant/chat",
        headers=owner["headers"],
        json={"message": "Explain authentication"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "answer": "Authentication is handled by auth/service.py [1]",
        "sources": [{"file": "auth/service.py", "start_line": 45, "end_line": 93}],
    }
    assert len(calls) == 1
    assert str(calls[0][0]) == project["id"]
    assert calls[0][1] == "Explain authentication"
    assert calls[0][2] == 5


def test_assistant_chat_multiple_sources_use_public_metadata(monkeypatch, client, authenticated_user):
    owner = authenticated_user()
    _, project = create_workspace_project(client, owner, "Assistant sources project")

    monkeypatch.setattr(
        RAGService,
        "ask",
        lambda self, project_id, message, limit: {
            "answer": "Authentication spans auth/service.py and auth/tokens.py. [1][2]",
            "sources": [
                {"file_path": "auth/service.py", "start_line": 45, "end_line": 93},
                {"file_path": "auth/tokens.py", "start_line": 20, "end_line": 40},
            ],
            "retrieval_count": 2,
            "model_name": "private-model-name",
        },
    )

    response = client.post(
        f"/projects/{project['id']}/assistant/chat",
        headers=owner["headers"],
        json={"message": "Explain authentication completely"},
    )
    assert response.status_code == 200
    assert set(response.json()) == {"answer", "sources"}
    assert response.json()["sources"] == [
        {"file": "auth/service.py", "start_line": 45, "end_line": 93},
        {"file": "auth/tokens.py", "start_line": 20, "end_line": 40},
    ]
    assert "private-model-name" not in response.text


def test_assistant_chat_authorizes_project_viewer(monkeypatch, client, authenticated_user):
    owner = authenticated_user()
    workspace, project = create_workspace_project(client, owner, "Assistant viewer project")
    viewer = authenticated_user()
    added = client.post(
        f"/memberships/{workspace['id']}",
        headers=owner["headers"],
        json={"user_id": viewer["user"]["id"], "role": "VIEWER"},
    )
    assert added.status_code == 201
    monkeypatch.setattr(
        RAGService,
        "ask",
        lambda self, project_id, message, limit: {
            "answer": "The available indexed code does not establish an answer to this question.",
            "sources": [],
            "retrieval_count": 0,
            "model_name": "test-model",
        },
    )

    response = client.post(
        f"/projects/{project['id']}/assistant/chat",
        headers=viewer["headers"],
        json={"message": "How does billing work?"},
    )
    assert response.status_code == 200
    assert response.json()["sources"] == []
    assert "does not establish" in response.json()["answer"]


def test_assistant_chat_denies_workspace_non_member(client, authenticated_user):
    owner = authenticated_user()
    _, project = create_workspace_project(client, owner, "Private assistant project")
    outsider = authenticated_user()

    response = client.post(
        f"/projects/{project['id']}/assistant/chat",
        headers=outsider["headers"],
        json={"message": "authentication"},
    )
    assert response.status_code == 403


def test_assistant_chat_prevents_access_to_another_project(monkeypatch, client, authenticated_user):
    owner = authenticated_user()
    _, own_project = create_workspace_project(client, owner, "Own assistant project")
    _, other_project = create_workspace_project(client, owner, "Other assistant project")

    monkeypatch.setattr(
        RAGService,
        "ask",
        lambda self, project_id, message, limit: {
            "answer": "Grounded answer",
            "sources": [{"file_path": "own.py", "start_line": 1, "end_line": 2}],
            "retrieval_count": 1,
            "model_name": "test-model",
        },
    )

    response = client.post(
        f"/projects/{other_project['id']}/assistant/chat",
        headers=owner["headers"],
        json={"message": "Other project question"},
    )
    assert response.status_code == 200
    assert response.json()["sources"][0]["file"] == "own.py"

    response = client.post(
        f"/projects/{own_project['id']}/assistant/chat",
        headers=owner["headers"],
        json={"message": "Own project question"},
    )
    assert response.status_code == 200


@pytest.mark.parametrize(
    ("status", "detail"),
    [
        (429, "The LLM provider rate limit was exceeded."),
        (503, "LLM provider is not configured"),
        (504, "LLM provider timed out"),
        (502, "LLM provider request failed"),
    ],
)
def test_assistant_chat_propagates_rag_errors(monkeypatch, client, authenticated_user, status, detail):
    owner = authenticated_user()
    _, project = create_workspace_project(client, owner, "Assistant error project")

    def fake_ask(self, project_id, message, limit):
        raise HTTPException(status_code=status, detail=detail)

    monkeypatch.setattr(RAGService, "ask", fake_ask)
    response = client.post(
        f"/projects/{project['id']}/assistant/chat",
        headers=owner["headers"],
        json={"message": "Explain authentication"},
    )
    assert response.status_code == status
    assert response.json()["detail"] == detail


def test_assistant_chat_http_acceptance_end_to_end(monkeypatch, client, db_session, authenticated_user):
    from app.main import app

    owner = authenticated_user()
    _, project = create_workspace_project(client, owner, "Assistant HTTP acceptance")
    project_id = UUID(project["id"])

    repository = Repository(
        project_id=project_id,
        owner="acme",
        name="acceptance",
        url="https://github.com/acme/acceptance",
        status=RepositoryStatus.COMPLETED,
        commit_sha="a" * 40,
        file_count=1,
    )
    db_session.add(repository)
    db_session.flush()
    repository_file = RepositoryFile(
        repository_id=repository.id,
        path="auth/service.py",
        language="python",
        size_bytes=112,
        content_hash="b" * 64,
    )
    db_session.add(repository_file)
    db_session.flush()
    chunk = CodeChunk(
        file_id=repository_file.id,
        symbol="refresh_session",
        symbol_type="function",
        parent_symbol=None,
        start_line=85,
        end_line=112,
        content="def refresh_session():\n    rotate_refresh_token()\n",
        language="python",
        chunk_index=0,
        embedding=[1.0] + [0.0] * 383,
        embedding_status="COMPLETED",
        embedding_model=settings.EMBEDDING_MODEL_NAME,
    )
    db_session.add(chunk)
    db_session.commit()

    schema = app.openapi()
    path = "/projects/{project_id}/assistant/chat"
    operation = schema["paths"][path]["post"]
    request_schema_name = operation["requestBody"]["content"]["application/json"]["schema"]["$ref"].rsplit("/", 1)[-1]
    response_schema_name = operation["responses"]["200"]["content"]["application/json"]["schema"]["$ref"].rsplit("/", 1)[-1]
    request_schema = schema["components"]["schemas"][request_schema_name]
    response_schema = schema["components"]["schemas"][response_schema_name]
    assert set(request_schema["properties"]) == {"message"}
    assert request_schema["properties"]["message"]["minLength"] == 1
    assert request_schema["properties"]["message"]["maxLength"] == 4000
    assert set(response_schema["properties"]) == {"answer", "sources"}

    retrieval_mode = {"value": "grounded"}
    llm_calls = {"count": 0}

    def acceptance_search(self, requested_project_id, query, limit=5):
        if UUID(str(requested_project_id)) != project_id:
            return {"query": query.strip(), "model_name": self.model_name, "total": 0, "results": []}
        if retrieval_mode["value"] == "insufficient":
            return {"query": query.strip(), "model_name": self.model_name, "total": 0, "results": []}
        return {
            "query": query.strip(),
            "model_name": self.model_name,
            "total": 1,
            "results": [{
                "chunk_id": chunk.id,
                "repository_id": repository.id,
                "file_path": repository_file.path,
                "symbol": chunk.symbol,
                "symbol_type": chunk.symbol_type,
                "start_line": chunk.start_line,
                "end_line": chunk.end_line,
                "language": chunk.language,
                "similarity": 0.91,
                "snippet": chunk.content,
            }],
        }

    def acceptance_llm_generate(self, prompt):
        llm_calls["count"] += 1
        if retrieval_mode["value"] == "unsupported":
            return '{"answer_type":"answer","claims":[{"text":"Payment processing is implemented in billing.py","citation_ids":[99]}]}'
        return '{"answer_type":"answer","claims":[{"text":"Refresh token rotation is implemented in auth/service.py","citation_ids":[1]}]}'

    monkeypatch.setattr(SemanticSearchService, "search", acceptance_search)
    monkeypatch.setattr(OpenAICompatibleLLMProvider, "generate", acceptance_llm_generate)

    for payload in ({}, {"message": ""}, {"message": "   "}, {"message": "x" * 4001}, []):
        validation = client.post(
            f"/projects/{project_id}/assistant/chat",
            headers=owner["headers"],
            json=payload,
        )
        assert validation.status_code == 422

    grounded = client.post(
        f"/projects/{project_id}/assistant/chat",
        headers=owner["headers"],
        json={"message": "Where is refresh token rotation implemented?"},
    )
    assert grounded.status_code == 200, grounded.text
    assert set(grounded.json()) == {"answer", "sources"}
    assert grounded.json() == {
        "answer": "Refresh token rotation is implemented in auth/service.py [1]",
        "sources": [{
            "file": repository_file.path,
            "start_line": chunk.start_line,
            "end_line": chunk.end_line,
        }],
    }
    assert repository_file.path == "auth/service.py"
    assert chunk.start_line == 85
    assert chunk.end_line == 112
    assert llm_calls["count"] == 1
    public_text = grounded.text.lower()
    for forbidden in ("chunk_id", "repository_id", "embedding", "prompt", "model_name", "api_key", "provider"):
        assert forbidden not in public_text

    outsider = authenticated_user()
    denied = client.post(
        f"/projects/{project_id}/assistant/chat",
        headers=outsider["headers"],
        json={"message": "Where is refresh token rotation implemented?"},
    )
    assert denied.status_code == 403
    assert llm_calls["count"] == 1

    retrieval_mode["value"] = "insufficient"
    insufficient = client.post(
        f"/projects/{project_id}/assistant/chat",
        headers=owner["headers"],
        json={"message": "What handles quantum teleportation?"},
    )
    assert insufficient.status_code == 200
    assert insufficient.json()["sources"] == []
    assert "does not establish" in insufficient.json()["answer"]
    assert llm_calls["count"] == 1

    retrieval_mode["value"] = "unsupported"
    unsupported = client.post(
        f"/projects/{project_id}/assistant/chat",
        headers=owner["headers"],
        json={"message": "Where is billing implemented?"},
    )
    assert unsupported.status_code == 502
    assert "unsupported source" in unsupported.json()["detail"]
