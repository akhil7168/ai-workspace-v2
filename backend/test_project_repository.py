from app.db.session import SessionLocal
from app.models.project import Project, ProjectStatus
from app.repositories.project_repository import ProjectRepository


# Replace these with IDs from your current database.
TEST_WORKSPACE_ID = " 5cbf5a81-0b32-4802-aa9f-c0e0ed09e0da "
TEST_USER_ID = "d60fcdeb-5a9f-48d8-b56f-be7383ab88b9"


def test_create_and_read_project():
    db = SessionLocal()

    try:
        repo = ProjectRepository(db)

        project = Project(
            title="Sprint 5 Repository Test",
            description="Testing project foundation",
            status=ProjectStatus.ACTIVE,
            workspace_id=TEST_WORKSPACE_ID,
            created_by=TEST_USER_ID,
        )

        created = repo.create(project)

        assert created.id is not None
        assert created.title == "Sprint 5 Repository Test"

        fetched = repo.get_by_id(
            created.id
        )

        assert fetched is not None
        assert fetched.id == created.id

    finally:
        db.close()


def test_project_repository_crud():
    db = SessionLocal()

    try:
        repo = ProjectRepository(db)

        # CREATE
        project = Project(
            title="Sprint 5 CRUD Test",
            description="Repository CRUD test",
            status=ProjectStatus.ACTIVE,
            workspace_id=TEST_WORKSPACE_ID,
            created_by=TEST_USER_ID,
        )

        created = repo.create(project)

        assert created.id is not None

        # READ
        fetched = repo.get_by_id(
            created.id
        )

        assert fetched is not None
        assert fetched.id == created.id

        # LIST
        projects = repo.get_workspace_projects(
            TEST_WORKSPACE_ID
        )

        assert any(
            p.id == created.id
            for p in projects
        )

        # UPDATE
        fetched.title = "Updated Sprint 5 Project"

        updated = repo.update(
            fetched
        )

        assert updated.title == (
            "Updated Sprint 5 Project"
        )

        # DELETE
        repo.delete(updated)

        deleted = repo.get_by_id(
            created.id
        )

        assert deleted is None

    finally:
        db.close()