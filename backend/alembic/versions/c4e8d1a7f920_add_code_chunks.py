"""add code chunks

Revision ID: c4e8d1a7f920
Revises: a9d4f2c8e731
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "c4e8d1a7f920"
down_revision: Union[str, Sequence[str], None] = "a9d4f2c8e731"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "code_chunks",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("file_id", sa.UUID(), nullable=False),
        sa.Column("symbol", sa.String(length=255), nullable=False),
        sa.Column("symbol_type", sa.String(length=50), nullable=False),
        sa.Column("parent_symbol", sa.String(length=255), nullable=True),
        sa.Column("start_line", sa.Integer(), nullable=False),
        sa.Column("end_line", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("language", sa.String(length=50), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["file_id"], ["repository_files.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("file_id", "chunk_index", name="uq_code_chunk_file_index"),
    )
    op.create_index("ix_code_chunks_file_id", "code_chunks", ["file_id"])
    op.create_index("ix_code_chunks_file_id_chunk_index", "code_chunks", ["file_id", "chunk_index"])


def downgrade() -> None:
    op.drop_index("ix_code_chunks_file_id_chunk_index", table_name="code_chunks")
    op.drop_index("ix_code_chunks_file_id", table_name="code_chunks")
    op.drop_table("code_chunks")
