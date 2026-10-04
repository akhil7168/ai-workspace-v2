from uuid import UUID
from typing import Any

from app.models.project_member import ProjectMember


class ProjectMemberRepository:
    def __init__(self, db: Any):
        self.db = db

    def create(self, member: ProjectMember):
        self.db.add(member)
        self.db.commit()
        self.db.refresh(member)
        return member

    def get(self, project_id: UUID, user_id: UUID):
        return (
            self.db.query(ProjectMember)
            .filter(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == user_id,
            )
            .first()
        )

    def get_project_members(self, project_id: UUID):
        return (
            self.db.query(ProjectMember)
            .filter(ProjectMember.project_id == project_id)
            .order_by(ProjectMember.joined_at.asc())
            .all()
        )

    def update(self, member: ProjectMember):
        self.db.commit()
        self.db.refresh(member)
        return member

    def delete(self, member: ProjectMember):
        self.db.delete(member)
        self.db.commit()