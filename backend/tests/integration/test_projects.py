from datetime import datetime, timezone
from uuid import UUID, uuid4

from app.models.project import Project


def create_workspace(client, account):
    response = client.post(
        "/workspaces",
        headers=account["headers"],
        json={"name": "Projects integration"},
    )
    assert response.status_code == 200, response.text
    return response.json()


def test_project_create_uses_authenticated_creator_and_workspace(
    client,
    authenticated_user,
):
    owner = authenticated_user()
    workspace = create_workspace(client, owner)
    supplied_creator = str(uuid4())

    response = client.post(
        f"/projects/workspace/{workspace['id']}",
        headers=owner["headers"],
        json={"title": "API project", "created_by": supplied_creator},
    )

    assert response.status_code == 200
    project = response.json()
    assert project["workspace_id"] == workspace["id"]
    assert project["created_by"] == owner["user"]["id"]
    assert project["status"] == "ACTIVE"


def test_project_crud_and_delete_archive_semantics(
    client,
    db_session,
    authenticated_user,
):
    owner = authenticated_user()
    workspace = create_workspace(client, owner)
    created = client.post(
        f"/projects/workspace/{workspace['id']}",
        headers=owner["headers"],
        json={"title": "Before update"},
    )
    project_id = created.json()["id"]

    retrieved = client.get(
        f"/projects/{project_id}",
        headers=owner["headers"],
    )
    assert retrieved.status_code == 200
    updated = client.put(
        f"/projects/{project_id}",
        headers=owner["headers"],
        json={"title": "After update", "description": "Updated"},
    )
    assert updated.status_code == 200
    assert updated.json()["title"] == "After update"
    assert updated.json()["description"] == "Updated"

    deleted = client.delete(
        f"/projects/{project_id}",
        headers=owner["headers"],
    )
    assert deleted.status_code == 200
    assert deleted.json() == {"message": "Project archived successfully"}
    project = db_session.get(Project, UUID(project_id))
    assert project is not None
    assert project.status.value == "ARCHIVED"
    assert client.get(
        f"/projects/{project_id}",
        headers=owner["headers"],
    ).status_code == 404
    assert client.get(
        f"/projects/workspace/{workspace['id']}",
        headers=owner["headers"],
    ).json() == []


def test_project_archive_route_sets_archived_status(
    client,
    db_session,
    authenticated_user,
):
    owner = authenticated_user()
    workspace = create_workspace(client, owner)
    project = client.post(
        f"/projects/workspace/{workspace['id']}",
        headers=owner["headers"],
        json={"title": "Patch archive"},
    ).json()

    response = client.patch(
        f"/projects/{project['id']}/archive",
        headers=owner["headers"],
    )

    assert response.status_code == 200
    assert response.json()["status"] == "ARCHIVED"
    assert db_session.get(Project, UUID(project["id"])) is not None


def test_project_member_role_can_create_and_update_projects(
    client,
    authenticated_user,
):
    owner = authenticated_user()
    member = authenticated_user()
    workspace = create_workspace(client, owner)
    added = client.post(
        f"/memberships/{workspace['id']}",
        headers=owner["headers"],
        json={"user_id": member["user"]["id"], "role": "MEMBER"},
    )
    assert added.status_code == 201

    created = client.post(
        f"/projects/workspace/{workspace['id']}",
        headers=member["headers"],
        json={"title": "Member-created"},
    )
    assert created.status_code == 200
    updated = client.put(
        f"/projects/{created.json()['id']}",
        headers=member["headers"],
        json={"title": "Member-updated"},
    )
    assert updated.status_code == 200
    assert updated.json()["title"] == "Member-updated"


def test_project_workspace_listing_excludes_archived_and_paginates(
    client,
    db_session,
    authenticated_user,
):
    owner = authenticated_user()
    workspace = create_workspace(client, owner)
    created = []
    for index in range(3):
        response = client.post(
            f"/projects/workspace/{workspace['id']}",
            headers=owner["headers"],
            json={"title": f"Project {index}"},
        )
        assert response.status_code == 200
        created.append(response.json())

    for index, project_data in enumerate(created):
        project = db_session.get(Project, UUID(project_data["id"]))
        project.created_at = datetime(
            2025,
            1,
            index + 1,
            tzinfo=timezone.utc,
        )
    db_session.commit()

    archived = client.patch(
        f"/projects/{created[1]['id']}/archive",
        headers=owner["headers"],
    )
    assert archived.status_code == 200

    page = client.get(
        f"/projects/workspace/{workspace['id']}?limit=1&offset=1",
        headers=owner["headers"],
    )
    assert page.status_code == 200
    assert [project["id"] for project in page.json()] == [created[0]["id"]]


def test_project_boundaries_invalid_ids_archived_workspace_and_validation(
    client,
    authenticated_user,
):
    owner = authenticated_user()
    workspace = create_workspace(client, owner)

    assert client.get(
        f"/projects/{uuid4()}",
        headers=owner["headers"],
    ).status_code == 404
    assert client.get(
        "/projects/not-a-uuid",
        headers=owner["headers"],
    ).status_code == 422
    assert client.post(
        f"/projects/workspace/{workspace['id']}",
        headers=owner["headers"],
        json={"title": ""},
    ).status_code == 422
    assert client.get(
        f"/projects/workspace/{workspace['id']}?limit=101",
        headers=owner["headers"],
    ).status_code == 422

    client.delete(
        f"/workspaces/{workspace['id']}",
        headers=owner["headers"],
    )
    create_in_archived = client.post(
        f"/projects/workspace/{workspace['id']}",
        headers=owner["headers"],
        json={"title": "Blocked"},
    )
    list_archived = client.get(
        f"/projects/workspace/{workspace['id']}",
        headers=owner["headers"],
    )
    assert create_in_archived.status_code == 404
    assert list_archived.status_code == 404
