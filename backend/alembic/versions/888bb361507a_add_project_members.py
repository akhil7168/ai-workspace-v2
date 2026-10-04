"""add project members

Revision ID: 888bb361507a
Revises: 15f71f06347e
"""

from typing import Sequence, Union

from alembic import op


revision: str = "888bb361507a"
down_revision: Union[str, Sequence[str], None] = "15f71f06347e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ---------------------------------------------------------
    # 1. Create projectrole enum only if it does not exist
    # ---------------------------------------------------------
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_type
                WHERE typname = 'projectrole'
            ) THEN
                CREATE TYPE projectrole AS ENUM (
                    'OWNER',
                    'ADMIN',
                    'MEMBER',
                    'VIEWER'
                );
            END IF;
        END
        $$;
        """
    )

    # ---------------------------------------------------------
    # 2. Create project_members table
    #
    # IMPORTANT:
    # Raw SQL is intentionally used here so SQLAlchemy does
    # NOT attempt to CREATE TYPE projectrole again.
    # ---------------------------------------------------------
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS project_members (
            project_id UUID NOT NULL,
            user_id UUID NOT NULL,
            role projectrole NOT NULL DEFAULT 'MEMBER'::projectrole,
            assigned_by UUID NULL,
            joined_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

            CONSTRAINT project_members_pkey
                PRIMARY KEY (project_id, user_id),

            CONSTRAINT project_members_project_id_fkey
                FOREIGN KEY (project_id)
                REFERENCES projects(id)
                ON DELETE CASCADE,

            CONSTRAINT project_members_user_id_fkey
                FOREIGN KEY (user_id)
                REFERENCES users(id)
                ON DELETE CASCADE,

            CONSTRAINT project_members_assigned_by_fkey
                FOREIGN KEY (assigned_by)
                REFERENCES users(id)
                ON DELETE SET NULL
        );
        """
    )

    # ---------------------------------------------------------
    # 3. Backfill existing projects
    #
    # Every existing project's creator becomes OWNER.
    # ---------------------------------------------------------
    op.execute(
        """
        INSERT INTO project_members (
            project_id,
            user_id,
            role,
            assigned_by,
            joined_at
        )
        SELECT
            p.id,
            p.created_by,
            'OWNER'::projectrole,
            p.created_by,
            COALESCE(p.created_at, NOW())
        FROM projects p
        WHERE p.created_by IS NOT NULL
        ON CONFLICT (project_id, user_id)
        DO NOTHING;
        """
    )


def downgrade() -> None:
    # Remove project membership table
    op.execute(
        """
        DROP TABLE IF EXISTS project_members;
        """
    )

    # Remove enum
    op.execute(
        """
        DROP TYPE IF EXISTS projectrole;
        """
    )