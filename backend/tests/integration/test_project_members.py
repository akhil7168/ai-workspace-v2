def test_creator_is_project_owner_and_can_manage_project_members(
    client,
    authenticated_user,
):
    owner = authenticated_user()
    member = authenticated_user()
    additional_member = authenticated_user()
    workspace = client.post(
        "/workspaces",
        headers=owner["headers"],
        json={"name": "Project members"},
    ).json()
    for account in (member, additional_member):
        response = client.post(
            f"/memberships/{workspace['id']}",
            headers=owner["headers"],
            json={"user_id": account["user"]["id"], "role": "MEMBER"},
        )
        assert response.status_code == 201

    project = client.post(
        f"/projects/workspace/{workspace['id']}",
        headers=owner["headers"],
        json={"title": "Managed project"},
    ).json()
    project_id = project["id"]

    initial_members = client.get(
        f"/projects/{project_id}/members",
        headers=owner["headers"],
    )
    assert initial_members.status_code == 200
    assert [
        (item["user_id"], item["role"])
        for item in initial_members.json()
    ] == [(owner["user"]["id"], "OWNER")]

    added = client.post(
        f"/projects/{project_id}/members",
        headers=owner["headers"],
        json={"user_id": member["user"]["id"], "role": "ADMIN"},
    )
    assert added.status_code == 200
    assert added.json()["assigned_by"] == owner["user"]["id"]
    duplicate = client.post(
        f"/projects/{project_id}/members",
        headers=owner["headers"],
        json={"user_id": member["user"]["id"], "role": "MEMBER"},
    )
    assert duplicate.status_code == 409

    admin_added = client.post(
        f"/projects/{project_id}/members",
        headers=member["headers"],
        json={"user_id": additional_member["user"]["id"], "role": "VIEWER"},
    )
    assert admin_added.status_code == 200
    demoted = client.patch(
        f"/projects/{project_id}/members/{additional_member['user']['id']}",
        headers=member["headers"],
        json={"role": "MEMBER"},
    )
    removed = client.delete(
        f"/projects/{project_id}/members/{additional_member['user']['id']}",
        headers=member["headers"],
    )
    assert demoted.status_code == 200
    assert removed.status_code == 200

    owner_demotion = client.patch(
        f"/projects/{project_id}/members/{owner['user']['id']}",
        headers=owner["headers"],
        json={"role": "MEMBER"},
    )
    owner_removal = client.delete(
        f"/projects/{project_id}/members/{owner['user']['id']}",
        headers=owner["headers"],
    )
    assert owner_demotion.status_code == 403
    assert owner_removal.status_code == 403


def test_project_member_viewer_cannot_manage_members_and_nonmember_is_denied(
    client,
    authenticated_user,
):
    owner = authenticated_user()
    viewer = authenticated_user()
    workspace_only = authenticated_user()
    workspace = client.post(
        "/workspaces",
        headers=owner["headers"],
        json={"name": "Project role checks"},
    ).json()
    for account in (viewer, workspace_only):
        added = client.post(
            f"/memberships/{workspace['id']}",
            headers=owner["headers"],
            json={"user_id": account["user"]["id"], "role": "MEMBER"},
        )
        assert added.status_code == 201

    project = client.post(
        f"/projects/workspace/{workspace['id']}",
        headers=owner["headers"],
        json={"title": "Role-protected project"},
    ).json()
    project_id = project["id"]
    project_viewer = client.post(
        f"/projects/{project_id}/members",
        headers=owner["headers"],
        json={"user_id": viewer["user"]["id"], "role": "VIEWER"},
    )
    assert project_viewer.status_code == 200

    visible = client.get(
        f"/projects/{project_id}/members",
        headers=viewer["headers"],
    )
    assert visible.status_code == 200
    assert len(visible.json()) == 2

    for response in (
        client.post(
            f"/projects/{project_id}/members",
            headers=viewer["headers"],
            json={"user_id": workspace_only["user"]["id"], "role": "MEMBER"},
        ),
        client.patch(
            f"/projects/{project_id}/members/{viewer['user']['id']}",
            headers=viewer["headers"],
            json={"role": "MEMBER"},
        ),
        client.delete(
            f"/projects/{project_id}/members/{viewer['user']['id']}",
            headers=viewer["headers"],
        ),
    ):
        assert response.status_code == 403

    no_project_role = client.get(
        f"/projects/{project_id}/members",
        headers=workspace_only["headers"],
    )
    assert no_project_role.status_code == 403


def test_project_member_creation_requires_workspace_membership(
    client,
    authenticated_user,
):
    owner = authenticated_user()
    outsider = authenticated_user()
    workspace = client.post(
        "/workspaces",
        headers=owner["headers"],
        json={"name": "Workspace boundary"},
    ).json()
    project = client.post(
        f"/projects/workspace/{workspace['id']}",
        headers=owner["headers"],
        json={"title": "Workspace boundary project"},
    ).json()

    response = client.post(
        f"/projects/{project['id']}/members",
        headers=owner["headers"],
        json={"user_id": outsider["user"]["id"], "role": "MEMBER"},
    )

    assert response.status_code == 403
