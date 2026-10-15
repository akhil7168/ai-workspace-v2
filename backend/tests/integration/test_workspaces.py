from uuid import UUID

from app.models.workspace_member import WorkspaceRole
from app.repositories.workspace_member_repository import (
    WorkspaceMemberRepository,
)


def test_workspace_create_list_and_owner_membership(
    client,
    db_session,
    authenticated_user,
):
    owner = authenticated_user()
    created = client.post(
        "/workspaces",
        headers=owner["headers"],
        json={"name": "API workspace", "description": "Integration test"},
    )

    assert created.status_code == 200
    workspace = created.json()
    assert workspace["owner_id"] == owner["user"]["id"]
    assert workspace["is_archived"] is False
    membership = WorkspaceMemberRepository(db_session).get_membership(
        UUID(workspace["id"]),
        UUID(owner["user"]["id"]),
    )
    assert membership is not None
    assert membership.role == WorkspaceRole.OWNER

    listed = client.get("/workspaces", headers=owner["headers"])
    assert listed.status_code == 200
    assert [item["id"] for item in listed.json()] == [workspace["id"]]


def test_workspace_retrieve_update_archive_and_archived_visibility(
    client,
    authenticated_user,
):
    owner = authenticated_user()
    created = client.post(
        "/workspaces",
        headers=owner["headers"],
        json={"name": "Before archive"},
    )
    workspace_id = created.json()["id"]

    retrieved = client.get(
        f"/workspaces/{workspace_id}",
        headers=owner["headers"],
    )
    assert retrieved.status_code == 200

    updated = client.put(
        f"/workspaces/{workspace_id}",
        headers=owner["headers"],
        json={"name": "After update"},
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "After update"

    archived = client.delete(
        f"/workspaces/{workspace_id}",
        headers=owner["headers"],
    )
    assert archived.status_code == 200
    assert archived.json() == {"message": "Workspace archived successfully"}
    assert client.get(
        f"/workspaces/{workspace_id}",
        headers=owner["headers"],
    ).status_code == 404
    assert client.get("/workspaces", headers=owner["headers"]).json() == []


def test_workspace_access_and_delete_permissions(client, authenticated_user):
    owner = authenticated_user()
    outsider = authenticated_user()
    created = client.post(
        "/workspaces",
        headers=owner["headers"],
        json={"name": "Owner-only"},
    )
    workspace_id = created.json()["id"]

    hidden = client.get(
        f"/workspaces/{workspace_id}",
        headers=outsider["headers"],
    )
    forbidden_delete = client.delete(
        f"/workspaces/{workspace_id}",
        headers=outsider["headers"],
    )

    assert hidden.status_code == 404
    assert forbidden_delete.status_code == 404
    assert client.get(f"/workspaces/{workspace_id}").status_code == 401


def test_owner_can_add_member_and_member_can_view_but_not_archive_workspace(
    client,
    authenticated_user,
):
    owner = authenticated_user()
    member = authenticated_user()
    workspace = client.post(
        "/workspaces",
        headers=owner["headers"],
        json={"name": "Membership"},
    ).json()
    added = client.post(
        f"/memberships/{workspace['id']}",
        headers=owner["headers"],
        json={
            "user_id": member["user"]["id"],
            "role": "MEMBER",
        },
    )
    assert added.status_code == 201

    retrieved = client.get(
        f"/workspaces/{workspace['id']}",
        headers=member["headers"],
    )
    update = client.put(
        f"/workspaces/{workspace['id']}",
        headers=member["headers"],
        json={"is_archived": True},
    )
    delete = client.delete(
        f"/workspaces/{workspace['id']}",
        headers=member["headers"],
    )

    assert retrieved.status_code == 200
    assert update.status_code == 403
    assert delete.status_code == 403


def test_workspace_invalid_ids_payloads_and_pagination_are_validated(
    client,
    authenticated_user,
):
    owner = authenticated_user()
    assert client.get(
        "/workspaces/not-a-uuid",
        headers=owner["headers"],
    ).status_code == 422
    assert client.post(
        "/workspaces",
        headers=owner["headers"],
        json={"name": ""},
    ).status_code == 422
    assert client.get(
        "/workspaces?limit=0",
        headers=owner["headers"],
    ).status_code == 422
    assert client.get(
        "/workspaces?offset=-1",
        headers=owner["headers"],
    ).status_code == 422
