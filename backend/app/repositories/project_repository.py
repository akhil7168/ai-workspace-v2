from uuid import UUID
from typing import Any

from app.models.project import Project, ProjectStatus


class ProjectRepository:

    def __init__(self, db: Any):
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

    def get_workspace_projects(self, workspace_id: UUID):
        return (
            self.db.query(Project)
            .filter(Project.workspace_id == workspace_id)
            .order_by(Project.created_at.desc())
            .all()
        )

    def update(self, project: Project):
        self.db.commit()
        self.db.refresh(project)
        return project

    def delete(self, project: Project):
        self.db.delete(project)
        self.db.commit()