"""add chunk embeddings

Revision ID: d7b2e4f8a610
Revises: c4e8d1a7f920
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


revision: str = "d7b2e4f8a610"
down_revision: Union[str, Sequence[str], None] = "c4e8d1a7f920"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.add_column("code_chunks", sa.Column("embedding", Vector(384), nullable=True))
    op.add_column("code_chunks", sa.Column("embedding_model", sa.String(length=255), nullable=True))
    op.add_column("code_chunks", sa.Column("embedding_status", sa.String(length=20), nullable=True))
    op.add_column("code_chunks", sa.Column("embedded_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("code_chunks", "embedded_at")
    op.drop_column("code_chunks", "embedding_status")
    op.drop_column("code_chunks", "embedding_model")
    op.drop_column("code_chunks", "embedding")
    # The shared vector extension is intentionally retained because another
    # application table or extension user may depend on it.
