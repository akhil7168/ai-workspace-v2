from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.core.auth import get_current_user
from app.main import app
from app.models.workspace_member import WorkspaceRole
from app.schemas.project import ProjectCreate
from app.schemas.workspace import WorkspaceCreate
from app.services.project_service import ProjectService
from app.services.workspace_member_service import WorkspaceMemberService
from app.services.workspace_service import WorkspaceService


@pytest.fixture
def rbac_data(db_session, user_factory, client):
    db = db_session
    users = {
        name: user_factory(full_name=f"RBAC {name}")
        for name in ("owner", "member", "viewer", "outsider")
    }

    workspace = WorkspaceService(db).create_workspace(
        WorkspaceCreate(name="RBAC workspace"),
        users["owner"].id,
    )
    WorkspaceMemberService(db).add_member(
        workspace.id,
        users["member"].id,
        WorkspaceRole.MEMBER,
    )
    WorkspaceMemberService(db).add_member(
        workspace.id,
        users["viewer"].id,
        WorkspaceRole.VIEWER,
    )
    outsider_workspace = WorkspaceService(db).create_workspace(
        WorkspaceCreate(name="Outsider workspace"),
        users["outsider"].id,
    )
    project = ProjectService(db).create_project(
        workspace.id,
        ProjectCreate(title="RBAC project"),
        users["owner"].id,
    )

    def act_as(user_name: str):
        user_id = users[user_name].id
        app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(
            id=user_id
        )

    data = {
        "db": db,
        "users": users,
        "workspace": workspace,
        "outsider_workspace": outsider_workspace,
        "project": project,
        "act_as": act_as,
        "client": client,
    }
    try:
        yield data
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.parametrize("user_name", ["owner", "member"])
def test_workspace_owner_and_member_can_retrieve_project(rbac_data, user_name):
    rbac_data["act_as"](user_name)

    response = rbac_data["client"].get(
        f"/projects/{rbac_data['project'].id}"
    )

    assert response.status_code == 200, response.text
    assert response.json()["id"] == str(rbac_data["project"].id)


def test_unrelated_user_cannot_retrieve_project(rbac_data):
    rbac_data["act_as"]("outsider")

    response = rbac_data["client"].get(
        f"/projects/{rbac_data['project'].id}"
    )

    assert response.status_code == 403


@pytest.mark.parametrize(
    ("method", "path", "payload"),
    [
        ("put", "/projects/{project_id}", {"title": "Unauthorized"}),
        ("patch", "/projects/{project_id}/archive", None),
        ("delete", "/projects/{project_id}", None),
    ],
)
def test_unrelated_user_cannot_modify_project(
    rbac_data,
    method,
    path,
    payload,
):
    rbac_data["act_as"]("outsider")
    path = path.format(project_id=rbac_data["project"].id)

    response = getattr(rbac_data["client"], method)(
        path,
        json=payload,
    ) if payload is not None else getattr(rbac_data["client"], method)(path)

    assert response.status_code == 403


@pytest.mark.parametrize(
    ("method", "path_template", "payload"),
    [
        (
            "post",
            "/projects/workspace/{workspace_id}",
            {"title": "Viewer project"},
        ),
        (
            "put",
            "/projects/{project_id}",
            {"title": "Viewer update"},
        ),
        ("delete", "/projects/{project_id}", None),
    ],
)
def test_viewer_cannot_create_update_or_delete_projects(
    rbac_data,
    method,
    path_template,
    payload,
):
    rbac_data["act_as"]("viewer")
    path = path_template.format(
        workspace_id=rbac_data["workspace"].id,
        project_id=rbac_data["project"].id,
    )

    response = getattr(rbac_data["client"], method)(
        path,
        json=payload,
    ) if payload is not None else getattr(rbac_data["client"], method)(path)

    assert response.status_code == 403


def test_owner_can_create_and_update_project(rbac_data):
    rbac_data["act_as"]("owner")

    create_response = rbac_data["client"].post(
        f"/projects/workspace/{rbac_data['workspace'].id}",
        json={"title": "Owner-created project"},
    )
    assert create_response.status_code == 200, create_response.text

    update_response = rbac_data["client"].put(
        f"/projects/{create_response.json()['id']}",
        json={"title": "Owner-updated project"},
    )
    assert update_response.status_code == 200, update_response.text
    assert update_response.json()["title"] == "Owner-updated project"


def test_missing_project_returns_404(rbac_data):
    rbac_data["act_as"]("owner")

    response = rbac_data["client"].get(f"/projects/{uuid4()}")

    assert response.status_code == 404


@pytest.mark.parametrize(
    ("method", "path", "payload"),
    [
        ("get", "/projects/{project_id}", None),
        ("put", "/projects/{project_id}", {"title": "Unauthenticated"}),
        ("patch", "/projects/{project_id}/archive", None),
        ("delete", "/projects/{project_id}", None),
        (
            "post",
            "/projects/workspace/{workspace_id}",
            {"title": "Unauthenticated"},
        ),
        ("get", "/projects/workspace/{workspace_id}", None),
    ],
)
def test_project_endpoints_require_authentication(
    rbac_data,
    method,
    path,
    payload,
):
    path = path.format(
        project_id=rbac_data["project"].id,
        workspace_id=rbac_data["workspace"].id,
    )

    response = getattr(rbac_data["client"], method)(
        path,
        json=payload,
    ) if payload is not None else getattr(rbac_data["client"], method)(path)

    assert response.status_code == 401


def test_workspace_listing_returns_only_current_users_workspaces(rbac_data):
    rbac_data["act_as"]("outsider")

    response = rbac_data["client"].get("/workspaces")

    assert response.status_code == 200, response.text
    assert [item["id"] for item in response.json()] == [
        str(rbac_data["outsider_workspace"].id)
    ]


def test_workspace_member_cannot_delete_workspace(rbac_data):
    rbac_data["act_as"]("member")

    response = rbac_data["client"].delete(
        f"/workspaces/{rbac_data['workspace'].id}"
    )

    assert response.status_code == 403


def test_workspace_delete_service_returns_http_403_for_non_owner(rbac_data):
    with pytest.raises(HTTPException) as exception:
        WorkspaceService(rbac_data["db"]).delete_workspace(
            rbac_data["workspace"].id,
            rbac_data["users"]["member"].id,
        )

    assert exception.value.status_code == 403


def test_missing_workspace_returns_404_before_membership_check(rbac_data):
    rbac_data["act_as"]("owner")

    response = rbac_data["client"].get(f"/workspaces/{uuid4()}")

    assert response.status_code == 404


def test_user_without_workspace_access_receives_404(rbac_data):
    rbac_data["act_as"]("outsider")

    response = rbac_data["client"].get(
        f"/workspaces/{rbac_data['workspace'].id}"
    )

    assert response.status_code == 404
