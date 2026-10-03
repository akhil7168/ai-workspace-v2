from uuid import uuid4

from app.models.project import Project


def test_project_owner_is_creator():
    owner_id = uuid4()

    project = Project(
        title="Ownership Test",
        workspace_id=uuid4(),
        created_by=owner_id,
    )

    assert project.created_by == owner_id