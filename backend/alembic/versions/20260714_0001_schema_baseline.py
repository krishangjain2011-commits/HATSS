"""Establish Alembic schema version tracking without domain tables.

Revision ID: 20260714_0001
Revises:
Create Date: 2026-07-14
"""

revision = "20260714_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create no domain tables in the project-foundation milestone."""


def downgrade() -> None:
    """Revert no domain tables in the project-foundation milestone."""
