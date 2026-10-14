from uuid import UUID
from sqlalchemy.orm import Session

from app.models.project import Project, ProjectStatus


class ProjectRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, project: Project):
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def get_by_id(self, project_id: UUID):
        return (
            self.db.query(Project)
            .filter(Project.id == project_id)
            .first()
        )

    def get_workspace_projects(self, workspace_id: UUID, limit: int | None = None, offset: int = 0):
        query = (
            self.db.query(Project)
            .filter(
                Project.workspace_id == workspace_id,
                Project.status != ProjectStatus.ARCHIVED,
            )
            .order_by(Project.created_at.desc())
        )

        if offset:
            query = query.offset(offset)

        if limit is not None:
            query = query.limit(limit)

        return query.all()

    def update(self, project: Project):
        self.db.commit()
        self.db.refresh(project)
        return project

    def delete(self, project: Project):
        self.db.delete(project)
        self.db.commit()