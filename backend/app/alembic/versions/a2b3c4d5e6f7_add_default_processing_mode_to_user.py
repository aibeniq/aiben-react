"""Add default_processing_mode to user

Revision ID: a2b3c4d5e6f7
Revises: a1b2c3d4e5f7
Create Date: 2025-11-07 04:55:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision = "a2b3c4d5e6f7"
down_revision = "a1b2c3d4e5f7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Check if column already exists
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    columns = [col["name"] for col in inspector.get_columns("user")]

    if "default_processing_mode" not in columns:
        # Add default_processing_mode column to user table
        op.add_column(
            "user",
            sa.Column(
                "default_processing_mode",
                sa.String(length=20),
                nullable=False,
                server_default="vector",  # Default to vector search
            ),
        )


def downgrade() -> None:
    # Check if column exists before trying to drop it
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    columns = [col["name"] for col in inspector.get_columns("user")]

    if "default_processing_mode" in columns:
        # Remove default_processing_mode column from user table
        op.drop_column("user", "default_processing_mode")
