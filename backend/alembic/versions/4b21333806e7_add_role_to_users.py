from alembic import op
import sqlalchemy as sa

revision = "xxxxxxxx"
down_revision = "<previous_revision_id>"
branch_labels = None
depends_on = None


def upgrade():

    op.add_column(
        "users",
        sa.Column(
            "role",
            sa.String(length=20),
            nullable=False,
            server_default="USER",
        ),
    )


def downgrade():

    op.drop_column("users", "role")