from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.core.permissions import Permission
from app.core.security import create_refresh_token
from app.models.project import ProjectStatus
from app.models.session import UserSession
from app.models.workspace_member import WorkspaceRole
from app.schemas.project import ProjectCreate
from app.schemas.workspace import WorkspaceCreate
from app.services.permission_service import PermissionService
from app.services.project_service import ProjectService
from app.services.session_service import SessionService
from app.services.workspace_member_service import WorkspaceMemberService
from app.services.workspace_service import WorkspaceService


def test_workspace_roles_have_expected_project_permissions():
    assert PermissionService.has_permission(
        WorkspaceRole.OWNER,
        Permission.PROJECT_DELETE,
    )
    assert PermissionService.has_permission(
        WorkspaceRole.MEMBER,
        Permission.PROJECT_UPDATE,
    )
    assert not PermissionService.has_permission(
        WorkspaceRole.VIEWER,
        Permission.PROJECT_CREATE,
    )

    with pytest.raises(HTTPException) as denied:
        PermissionService.require_permission(
            WorkspaceRole.VIEWER,
            Permission.PROJECT_UPDATE,
        )
    assert denied.value.status_code == 403


def test_workspace_member_service_rejects_duplicate_and_missing_users(
    db_session,
    user_factory,
):
    owner = user_factory()
    member = user_factory()
    workspace = WorkspaceService(db_session).create_workspace(
        WorkspaceCreate(name="Membership checks"),
        owner.id,
    )
    service = WorkspaceMemberService(db_session)

    membership = service.add_member(
        workspace.id,
        member.id,
        WorkspaceRole.MEMBER,
    )
    assert membership.role == WorkspaceRole.MEMBER

    with pytest.raises(HTTPException) as duplicate:
        service.add_member(
            workspace.id,
            member.id,
            WorkspaceRole.MEMBER,
        )
    with pytest.raises(HTTPException) as missing_user:
        service.add_member(
            workspace.id,
            uuid4(),
            WorkspaceRole.MEMBER,
        )

    assert duplicate.value.status_code == 409
    assert missing_user.value.status_code == 404


def test_refresh_session_rotation_and_revocation(db_session, user_factory):
    user = user_factory()
    service = SessionService(db_session)
    original_token = create_refresh_token(str(user.id))
    service.create_session(user.id, original_token)

    rotated = service.rotate_refresh_token(original_token)

    assert rotated is not None
    session, new_token = rotated
    assert session.refresh_token == new_token
    assert new_token != original_token
    assert service.rotate_refresh_token(original_token) is None
    assert service.revoke_session(new_token)
    assert not service.revoke_session(new_token)
    assert service.rotate_refresh_token(new_token) is None


def test_expired_refresh_session_is_revoked(db_session, user_factory):
    from app.repositories.session_repository import SessionRepository

    user = user_factory()
    session = UserSession(
        user_id=user.id,
        refresh_token=create_refresh_token(str(user.id)),
        expires_at=datetime.now(timezone.utc) - timedelta(minutes=1),
        is_revoked=False,
    )
    SessionRepository(db_session).create(session)

    assert SessionService(db_session).rotate_refresh_token(
        session.refresh_token
    ) is None
    assert session.is_revoked is True


def test_refresh_rotation_rolls_back_and_reraises_repository_errors(
    db_session,
    user_factory,
    monkeypatch,
):
    user = user_factory()
    token = create_refresh_token(str(user.id))
    service = SessionService(db_session)
    service.create_session(user.id, token)

    def fail_after_uncommitted_change(**_kwargs):
        db_session.query(UserSession).filter(
            UserSession.refresh_token == token
        ).update({UserSession.is_revoked: True})
        raise RuntimeError("rotation storage failure")

    monkeypatch.setattr(service.repo, "rotate", fail_after_uncommitted_change)

    with pytest.raises(RuntimeError, match="rotation storage failure"):
        service.rotate_refresh_token(token)

    persisted = (
        db_session.query(UserSession)
        .filter(UserSession.refresh_token == token)
        .one()
    )
    assert persisted.is_revoked is False


def test_workspace_and_project_services_exclude_archived_resources(
    db_session,
    user_factory,
):
    user = user_factory()
    workspace_service = WorkspaceService(db_session)
    project_service = ProjectService(db_session)
    workspace = workspace_service.create_workspace(
        WorkspaceCreate(name="Archive boundary"),
        user.id,
    )
    project = project_service.create_project(
        workspace.id,
        ProjectCreate(title="Archived project"),
        user.id,
    )
    project.status = ProjectStatus.ARCHIVED
    db_session.commit()

    assert workspace_service.list_workspaces(user.id) == [workspace]
    assert project_service.list_workspace_projects(workspace.id) == []
