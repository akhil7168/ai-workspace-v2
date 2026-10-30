"""add repositories and repository files

Revision ID: a9d4f2c8e731
Revises: 888bb361507a
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "a9d4f2c8e731"
down_revision: Union[str, Sequence[str], None] = "888bb361507a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "repositories",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("project_id", sa.UUID(), nullable=False),
        sa.Column("owner", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("url", sa.String(length=500), nullable=False),
        sa.Column("branch", sa.String(length=255), nullable=True),
        sa.Column("commit_sha", sa.String(length=40), nullable=True),
        sa.Column("status", sa.Enum("PENDING", "INGESTING", "COMPLETED", "FAILED", name="repository_status"), nullable=False, server_default="PENDING"),
        sa.Column("file_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_size_bytes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("indexed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "url", name="uq_repository_project_url"),
    )
    op.create_index("ix_repositories_project_id", "repositories", ["project_id"])
    op.create_index("ix_repositories_url", "repositories", ["url"])

    op.create_table(
        "repository_files",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("repository_id", sa.UUID(), nullable=False),
        sa.Column("path", sa.String(length=2048), nullable=False),
        sa.Column("language", sa.String(length=50), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["repository_id"], ["repositories.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("repository_id", "path", name="uq_repository_file_path"),
    )
    op.create_index("ix_repository_files_repository_id", "repository_files", ["repository_id"])


def downgrade() -> None:
    op.drop_index("ix_repository_files_repository_id", table_name="repository_files")
    op.drop_table("repository_files")
    op.drop_index("ix_repositories_url", table_name="repositories")
    op.drop_index("ix_repositories_project_id", table_name="repositories")
    op.drop_table("repositories")
    repository_status = sa.Enum(name="repository_status")
    repository_status.drop(op.get_bind(), checkfirst=True)
