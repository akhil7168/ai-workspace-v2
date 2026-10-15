from datetime import datetime, timezone
from uuid import uuid4

from app.models.project import Project, ProjectStatus
from app.models.session import UserSession
from app.models.user import User
from app.models.workspace import Workspace
from app.models.workspace_member import WorkspaceMember, WorkspaceRole
from app.repositories.project_repository import ProjectRepository
from app.repositories.session_repository import SessionRepository
from app.repositories.user_repository import UserRepository
from app.repositories.workspace_member_repository import (
    WorkspaceMemberRepository,
)
from app.repositories.workspace_repository import WorkspaceRepository


def test_user_repository_create_lookup_and_updates(db_session, user_factory):
    repository = UserRepository(db_session)
    user = User(
        full_name="Repository Test",
        email=f"{uuid4()}@example.com",
        password_hash="hashed_password",
    )
    repository.create(user)

    fetched = repository.get_by_email(user.email)
    assert fetched is not None
    assert fetched.id == user.id
    assert fetched.email == user.email
    assert fetched.full_name == "Repository Test"
    assert repository.get_by_id(user.id).email == user.email
    all_users = repository.get_all()
    assert isinstance(all_users, list)
    assert fetched in all_users

    updated = repository.update_profile(user, "Updated name", "updated@example.com")
    repository.update_password(updated, "new-hash")

    assert updated.full_name == "Updated name"
    assert updated.email == "updated@example.com"
    assert updated.password_hash == "new-hash"


def test_workspace_repository_filters_archived_and_paginates(
    db_session,
    user_factory,
):
    owner = user_factory()
    repository = WorkspaceRepository(db_session)
    for index in range(4):
        workspace = Workspace(
            owner_id=owner.id,
            name=f"Workspace {index}",
            is_archived=index == 2,
            created_at=datetime(2025, 1, index + 1, tzinfo=timezone.utc),
        )
        db_session.add(workspace)
    db_session.commit()

    result = repository.get_user_workspaces(owner.id, limit=2, offset=1)

    assert [workspace.name for workspace in result] == [
        "Workspace 1",
        "Workspace 0",
    ]


def test_project_repository_filters_archives_orders_and_paginates(
    db_session,
    user_factory,
):
    owner = user_factory()
    workspace = Workspace(owner_id=owner.id, name="Projects")
    db_session.add(workspace)
    db_session.commit()
    projects = [
        Project(
            workspace_id=workspace.id,
            created_by=owner.id,
            title=f"Project {index}",
            status=ProjectStatus.ARCHIVED if index == 2 else ProjectStatus.ACTIVE,
            created_at=datetime(2025, 1, index + 1, tzinfo=timezone.utc),
        )
        for index in range(4)
    ]
    db_session.add_all(projects)
    db_session.commit()

    result = ProjectRepository(db_session).get_workspace_projects(
        workspace.id,
        limit=2,
        offset=1,
    )

    assert [project.title for project in result] == ["Project 1", "Project 0"]


def test_membership_repository_filters_archived_workspaces_and_paginates(
    db_session,
    user_factory,
):
    owner = user_factory()
    member = user_factory()
    active = Workspace(owner_id=owner.id, name="Active")
    archived = Workspace(owner_id=owner.id, name="Archived", is_archived=True)
    db_session.add_all([active, archived])
    db_session.commit()
    db_session.add_all(
        [
            WorkspaceMember(
                workspace_id=active.id,
                user_id=member.id,
                role=WorkspaceRole.MEMBER,
            ),
            WorkspaceMember(
                workspace_id=archived.id,
                user_id=member.id,
                role=WorkspaceRole.MEMBER,
            ),
        ]
    )
    db_session.commit()

    result = WorkspaceMemberRepository(db_session).get_user_workspaces(
        member.id,
        limit=1,
        offset=0,
    )

    assert len(result) == 1
    assert result[0].workspace_id == active.id


def test_session_repository_distinguishes_active_and_revoked_tokens(
    db_session,
    user_factory,
):
    user = user_factory()
    active = UserSession(
        user_id=user.id,
        refresh_token="active-token",
        expires_at=datetime(2030, 1, 1, tzinfo=timezone.utc),
        is_revoked=False,
    )
    revoked = UserSession(
        user_id=user.id,
        refresh_token="revoked-token",
        expires_at=datetime(2030, 1, 1, tzinfo=timezone.utc),
        is_revoked=True,
    )
    db_session.add_all([active, revoked])
    db_session.commit()
    repository = SessionRepository(db_session)

    assert repository.get_by_refresh_token("revoked-token") is not None
    assert repository.get_active_by_refresh_token("revoked-token") is None
    assert repository.get_active_by_refresh_token("active-token") is not None
