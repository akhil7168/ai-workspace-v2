from uuid import UUID
from sqlalchemy.orm import Session

from app.models.repository import Repository


class RepositoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_project_and_url(self, project_id: UUID, url: str) -> Repository | None:
        return self.db.query(Repository).filter(
            Repository.project_id == project_id,
            Repository.url == url,
        ).first()

    def list_by_project(self, project_id: UUID) -> list[Repository]:
        return self.db.query(Repository).filter(
            Repository.project_id == project_id
        ).order_by(Repository.created_at.desc()).all()

    def get_by_project_and_id(self, project_id: UUID, repository_id: UUID) -> Repository | None:
        return self.db.query(Repository).filter(
            Repository.project_id == project_id,
            Repository.id == repository_id,
        ).first()

    def create(self, repository: Repository) -> Repository:
        self.db.add(repository)
        self.db.commit()
        self.db.refresh(repository)
        return repository

    def update(self, repository: Repository) -> Repository:
        self.db.commit()
        self.db.refresh(repository)
        return repository
