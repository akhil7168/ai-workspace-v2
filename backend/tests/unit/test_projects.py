from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.models.project import ProjectStatus
from app.models.project_member import ProjectRole
from app.repositories.project_member_repository import ProjectMemberRepository
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.schemas.workspace import WorkspaceCreate
from app.services.project_service import ProjectService
from app.services.workspace_service import WorkspaceService


def create_workspace(db_session, user):
    return WorkspaceService(db_session).create_workspace(
        WorkspaceCreate(name="Project workspace"),
        user.id,
    )


def test_create_project_sets_workspace_creator_and_active_status(
    db_session,
    user_factory,
):
    owner = user_factory()
    workspace = create_workspace(db_session, owner)

    project = ProjectService(db_session).create_project(
        workspace.id,
        ProjectCreate(title="Created project"),
        owner.id,
    )
    owner_membership = ProjectMemberRepository(db_session).get(
        project.id,
        owner.id,
    )

    assert project.workspace_id == workspace.id
    assert project.created_by == owner.id
    assert project.status == ProjectStatus.ACTIVE
    assert owner_membership is not None
    assert owner_membership.role == ProjectRole.OWNER
    assert owner_membership.assigned_by == owner.id


def test_project_creation_rejects_missing_or_archived_workspace(
    db_session,
    user_factory,
):
    owner = user_factory()
    service = ProjectService(db_session)
    with pytest.raises(HTTPException) as missing:
        service.create_project(
            uuid4(),
            ProjectCreate(title="No workspace"),
            owner.id,
        )

    workspace = create_workspace(db_session, owner)
    workspace.is_archived = True
    db_session.commit()
    with pytest.raises(HTTPException) as archived:
        service.create_project(
            workspace.id,
            ProjectCreate(title="Archived workspace"),
            owner.id,
        )

    assert missing.value.status_code == 404
    assert archived.value.status_code == 409


def test_project_update_and_delete_use_archived_status(
    db_session,
    user_factory,
):
    owner = user_factory()
    workspace = create_workspace(db_session, owner)
    service = ProjectService(db_session)
    project = service.create_project(
        workspace.id,
        ProjectCreate(title="Before"),
        owner.id,
    )

    updated = service.update_project(
        project.id,
        ProjectUpdate(title="After"),
        owner.id,
    )
    result = service.delete_project(project.id, owner.id)

    assert updated.title == "After"
    assert result == {"message": "Project archived successfully"}
    assert project.status == ProjectStatus.ARCHIVED
    assert db_session.get(type(project), project.id) is project

    with pytest.raises(HTTPException) as archived:
        service.get_project(project.id)
    assert archived.value.status_code == 404


def test_project_archive_endpoint_service_rejects_missing_project(
    db_session,
    user_factory,
):
    user = user_factory()

    with pytest.raises(HTTPException) as error:
        ProjectService(db_session).archive_project(uuid4(), user.id)

    assert error.value.status_code == 404


def test_project_owner_check_is_explicit_service_behavior(
    db_session,
    user_factory,
):
    creator = user_factory()
    other_user = user_factory()
    workspace = create_workspace(db_session, creator)
    project = ProjectService(db_session).create_project(
        workspace.id,
        ProjectCreate(title="Creator-owned"),
        creator.id,
    )
    service = ProjectService(db_session)

    assert service.require_owner(project.id, creator.id) is project
    with pytest.raises(HTTPException) as error:
        service.require_owner(project.id, other_user.id)
    assert error.value.status_code == 403
