from typing import Any

from app.models.workspace_member import WorkspaceMember, WorkspaceRole


class WorkspaceMemberRepository:

    def __init__(self, db: Any):
        self.db = db

    def add_member(self, member: WorkspaceMember):

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

    def get_user_workspaces(self, user_id):

        return (
            self.db.query(WorkspaceMember)
            .filter(
                WorkspaceMember.user_id == user_id
            )
            .all()
        )

    def update_role(self, member, role: WorkspaceRole):

        member.role = role

        self.db.commit()
        self.db.refresh(member)

        return member

    def remove_member(self, member):

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