from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.models.workspace_member import WorkspaceRole
from app.repositories.workspace_member_repository import (
    WorkspaceMemberRepository,
)
from app.schemas.workspace import WorkspaceCreate, WorkspaceUpdate
from app.services.workspace_service import WorkspaceService


def test_create_workspace_sets_owner_and_owner_membership(
    db_session,
    user_factory,
):
    owner = user_factory()
    workspace = WorkspaceService(db_session).create_workspace(
        WorkspaceCreate(name="Owned workspace"),
        owner.id,
    )
    membership = WorkspaceMemberRepository(db_session).get_membership(
        workspace.id,
        owner.id,
    )

    assert workspace.owner_id == owner.id
    assert membership is not None
    assert membership.role == WorkspaceRole.OWNER


def test_create_workspace_requires_existing_owner(db_session):
    with pytest.raises(HTTPException) as error:
        WorkspaceService(db_session).create_workspace(
            WorkspaceCreate(name="No owner"),
            uuid4(),
        )

    assert error.value.status_code == 404
    assert error.value.detail == "User not found"


def test_update_workspace_changes_fields_and_owner_can_archive(
    db_session,
    user_factory,
):
    owner = user_factory()
    service = WorkspaceService(db_session)
    workspace = service.create_workspace(
        WorkspaceCreate(name="Before"),
        owner.id,
    )

    updated = service.update_workspace(
        workspace.id,
        WorkspaceUpdate(name="After", is_archived=True),
        owner.id,
    )

    assert updated.name == "After"
    assert updated.is_archived is True


def test_non_owner_cannot_archive_workspace(db_session, user_factory):
    owner = user_factory()
    member = user_factory()
    service = WorkspaceService(db_session)
    workspace = service.create_workspace(
        WorkspaceCreate(name="Shared"),
        owner.id,
    )
    service.membership_service.add_member(
        workspace.id,
        member.id,
        WorkspaceRole.ADMIN,
    )

    with pytest.raises(HTTPException) as error:
        service.update_workspace(
            workspace.id,
            WorkspaceUpdate(is_archived=True),
            member.id,
        )

    assert error.value.status_code == 403
    assert workspace.is_archived is False


def test_workspace_delete_archives_instead_of_removing(
    db_session,
    user_factory,
):
    owner = user_factory()
    service = WorkspaceService(db_session)
    workspace = service.create_workspace(
        WorkspaceCreate(name="Archive me"),
        owner.id,
    )

    result = service.delete_workspace(workspace.id, owner.id)

    assert result == {"message": "Workspace archived successfully"}
    assert db_session.get(type(workspace), workspace.id) is workspace
    assert workspace.is_archived is True


def test_workspace_not_found_for_non_member_or_missing_id(
    db_session,
    user_factory,
):
    owner = user_factory()
    outsider = user_factory()
    workspace = WorkspaceService(db_session).create_workspace(
        WorkspaceCreate(name="Private"),
        owner.id,
    )

    with pytest.raises(HTTPException) as no_membership:
        WorkspaceService(db_session).get_workspace(workspace.id, outsider.id)
    with pytest.raises(HTTPException) as missing:
        WorkspaceService(db_session).get_workspace(uuid4(), owner.id)

    assert no_membership.value.status_code == 404
    assert missing.value.status_code == 404
