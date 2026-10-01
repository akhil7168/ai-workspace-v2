from typing import Any

from app.schemas import user
from fastapi import HTTPException # pyright: ignore[reportMissingImports]
from sqlalchemy.orm import Session # pyright: ignore[reportMissingImports]

from app.models.workspace_member import WorkspaceMember, WorkspaceRole
from app.repositories.workspace_member_repository import (
    WorkspaceMemberRepository,
)
from app.repositories.workspace_repository import WorkspaceRepository
from app.repositories.user_repository import UserRepository


class WorkspaceMemberService:

    def __init__(self, db: Session):

        self.db = db

        self.member_repo = WorkspaceMemberRepository(db)
        self.workspace_repo = WorkspaceRepository(db)
        self.user_repo = UserRepository(db)

    def add_member(
        self,
        workspace_id,
        user_id,
        role,
        invited_by=None,
    ):
        user = self.user_repo.get_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found",
            )

        existing = self.member_repo.get_membership(
            workspace_id=workspace_id,
            user_id=user_id,
        )

        if existing:
            raise HTTPException(
                status_code=409,
                detail="User is already a workspace member",
            )

        return self.member_repo.create_member(
            workspace_id=workspace_id,
            user_id=user_id,
            role=role,
            invited_by=invited_by,
        )

    def get_membership(
        self,
        workspace_id,
        user_id,
    ):
        return self.member_repo.get_membership(
            workspace_id=workspace_id,
            user_id=user_id,
        )

    def get_user_memberships(self, user_id):
        return self.member_repo.get_user_workspaces(user_id)

    

    def list_members(self, workspace_id):

        workspace = self.workspace_repo.get_by_id(workspace_id)

        if not workspace:
            raise HTTPException(404, "Workspace not found")

        return self.member_repo.get_workspace_members(workspace_id)

    def remove_member(
        self,
        workspace_id,
        user_id,
    ):
        membership = self.member_repo.get_membership(
            workspace_id=workspace_id,
            user_id=user_id,
        )

        if membership:
            self.member_repo.delete_member(membership)

        return {"message": "Member removed"}

    def update_role(
        self,
        workspace_id,
        user_id,
        role: WorkspaceRole,
    ):

        member = self.member_repo.get_membership(workspace_id, user_id)

        if not member:
            raise HTTPException(404, "Membership not found")

        return self.member_repo.update_role(member, role)

    def require_workspace_member(
        self,
        workspace_id,
        user_id,
    ):

        member = self.member_repo.get_membership(workspace_id, user_id)

        if not member:
            raise HTTPException(
            status_code=403,
        detail="User is not a workspace member",
    )

        return member

    def require_workspace_admin(
        self,
        workspace_id,
        user_id,
    ):

        member = self.require_workspace_member(workspace_id, user_id)

        if member.role not in (
            WorkspaceRole.OWNER,
            WorkspaceRole.ADMIN,
        ):
            raise HTTPException(
                403,
                "Admin permission required",
            )

        return member

    def workspace_size(self, workspace_id):

        return self.member_repo.count_workspace_members(workspace_id)