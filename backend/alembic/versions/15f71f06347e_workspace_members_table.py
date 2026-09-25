from alembic import op
import sqlalchemy as sa  # pyright: ignore[reportMissingImports]
from sqlalchemy.dialects import postgresql  # pyright: ignore[reportMissingImports]

revision = "15f71f06347e"
down_revision = "b89fc110ebbe"
branch_labels = None
depends_on = None


workspace_role = postgresql.ENUM(
    "OWNER",
    "ADMIN",
    "MEMBER",
    "VIEWER",
    name="workspace_role",
    create_type=False,
)


def upgrade():
    workspace_role.create(op.get_bind(), checkfirst=True)

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
            workspace_role,
            nullable=False,
            server_default="MEMBER",
        ),

        sa.Column(
            "joined_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("now()"),
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

        sa.PrimaryKeyConstraint(
            "workspace_id",
            "user_id",
        ),
    )


def downgrade():
    op.drop_table("workspace_members")

    workspace_role.drop(
        op.get_bind(),
        checkfirst=True,
    )