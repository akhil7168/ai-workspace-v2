from app.models.repository import Repository, RepositoryStatus
from app.utils.repository_ingestion import GitSnapshot, FileMetadata, GitHubCloneAdapter, RepositoryFileScanner


def create_workspace_project(client, account, title="Repository project"):
    workspace = client.post("/workspaces", headers=account["headers"], json={"name": "Repository workspace"})
    assert workspace.status_code == 200, workspace.text
    project = client.post(f"/projects/workspace/{workspace.json()['id']}", headers=account["headers"], json={"title": title})
    assert project.status_code == 200, project.text
    return workspace.json(), project.json()


def test_ingest_and_list_repository(monkeypatch, client, db_session, authenticated_user):
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
    listed = client.get(f"/projects/{project['id']}/repositories", headers=viewer["headers"])
    assert listed.status_code == 200
