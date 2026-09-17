from alembic import op
import sqlalchemy as sa  # pyright: ignore[reportMissingImports]

# revision identifiers
revision = "sync_users_schema_sprint6"
down_revision = "1f0b5e7d9a22"   # replace with your latest revision id
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "users",
        sa.Column(
            "is_verified",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )

    op.add_column(
        "users",
        sa.Column(
            "bio",
            sa.String(length=500),
            nullable=True,
        ),
    )

    op.add_column(
        "users",
        sa.Column(
            "avatar_url",
            sa.String(length=500),
            nullable=True,
        ),
    )


def downgrade():
    op.drop_column("users", "avatar_url")
    op.drop_column("users", "bio")
    op.drop_column("users", "is_verified")