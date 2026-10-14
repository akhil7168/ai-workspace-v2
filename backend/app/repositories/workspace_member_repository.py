from enum import member
from sqlalchemy.orm import Session

from app.models.workspace import Workspace
from app.models.workspace_member import WorkspaceMember, WorkspaceRole


class WorkspaceMemberRepository:

    def __init__(self, db: Session):
        self.db = db

    def add_member(self, member: WorkspaceMember):

        self.db.add(member)
        self.db.commit()
        self.db.refresh(member)

        return member

    def create_member(
        self,
        workspace_id,
        user_id,
        role,
        invited_by=None,
    ):
        member = WorkspaceMember(
            workspace_id=workspace_id,
            user_id=user_id,
            role=role,
            invited_by=invited_by,
        )

        self.db.add(member)
        self.db.commit()
        self.db.refresh(member)

        return member

    def get_membership(self, workspace_id, user_id):

        return (
            self.db.query(WorkspaceMember)
            .filter(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == user_id,
            )
            .first()
        )

    def get_workspace_members(self, workspace_id):

        return (
            self.db.query(WorkspaceMember)
            .filter(
                WorkspaceMember.workspace_id == workspace_id
            )
            .all()
        )

    def get_user_workspaces(self, user_id, limit: int | None = None, offset: int = 0):

        query = (
            self.db.query(WorkspaceMember)
            .join(Workspace, Workspace.id == WorkspaceMember.workspace_id)
            .filter(
                WorkspaceMember.user_id == user_id,
                Workspace.is_archived.is_(False),
            )
            .order_by(Workspace.created_at.desc())
        )

        if offset:
            query = query.offset(offset)

        if limit is not None:
            query = query.limit(limit)

        return query.all()

    def update_role(self, member, role: WorkspaceRole):

        member.role = role

        self.db.commit()
        self.db.refresh(member)

        return member

    def delete_member(self, member):

        self.db.delete(member)
        self.db.commit()

    def count_workspace_members(self, workspace_id):

        return (
            self.db.query(WorkspaceMember)
            .filter(
                WorkspaceMember.workspace_id == workspace_id
            )
            .count()
        )