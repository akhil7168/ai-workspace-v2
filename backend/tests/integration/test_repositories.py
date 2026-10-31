import os
from uuid import UUID

from app.models.repository import Repository, RepositoryFile, RepositoryStatus, CodeChunk
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
