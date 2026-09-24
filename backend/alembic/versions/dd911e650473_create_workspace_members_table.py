"""create_workspace_members_table

Revision ID: dd911e650473
Revises: b89fc110ebbe
Create Date: 2026-09-24 21:05:57.690841

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa  # type: ignore[import-not-found]
from sqlalchemy.dialects import postgresql  # type: ignore[import-not-found]


# revision identifiers, used by Alembic.
revision: str = 'dd911e650473'
down_revision: Union[str, Sequence[str], None] = 'b89fc110ebbe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():

    role_enum = postgresql.ENUM(
        "OWNER",
        "ADMIN",
        "MEMBER",
        "VIEWER",
        name="workspace_role_enum",
    )

    role_enum.create(op.get_bind(), checkfirst=True)
    workspace_role_enum = postgresql.ENUM(
        "OWNER",
        "ADMIN",
        "MEMBER",
        "VIEWER",
        name="workspace_role_enum",
        create_type=False,        # IMPORTANT
    )

    op.create_table(
        "workspace_members",

        sa.Column(
            "workspace_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        

        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),

        sa.Column(
            "role",
            role_enum,
            nullable=False,
            server_default="MEMBER",
        ),

        sa.Column(
            "invited_by",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),

        sa.Column(
            "joined_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),

        sa.PrimaryKeyConstraint(
            "workspace_id",
            "user_id",
            name="pk_workspace_members",
        ),

        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            ondelete="CASCADE",
        ),

        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),

        sa.ForeignKeyConstraint(
            ["invited_by"],
            ["users.id"],
            ondelete="SET NULL",
        ),
    )

    bind = op.get_bind()

    workspace_role_enum.create(bind, checkfirst=True)

    op.create_index(
        "idx_workspace_members_workspace",
        "workspace_members",
        ["workspace_id"],
    )

    op.create_index(
        "idx_workspace_members_user",
        "workspace_members",
        ["user_id"],
    )


def downgrade():

    op.drop_index("idx_workspace_members_workspace")
    op.drop_index("idx_workspace_members_user")

    op.drop_table("workspace_members")

    postgresql.ENUM(
        "OWNER",
        "ADMIN",
        "MEMBER",
        "VIEWER",
        name="workspace_role_enum",
    ).drop(op.get_bind(), checkfirst=True)
