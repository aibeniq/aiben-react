"""Add pdf_parsing_preference to user

Revision ID: a1b2c3d4e5f7
Revises: 483afa1509d2
Create Date: 2025-10-29 12:00:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f7"
down_revision = "483afa1509d2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Check if column already exists
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    columns = [col["name"] for col in inspector.get_columns("user")]

    if "pdf_parsing_preference" not in columns:
        # Add pdf_parsing_preference column to user table
        op.add_column(
            "user",
            sa.Column(
                "pdf_parsing_preference",
                sa.String(length=20),
                nullable=False,
                server_default="auto",  # Intelligent default for all users
            ),
        )


def downgrade() -> None:
    # Check if column exists before trying to drop it
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    columns = [col["name"] for col in inspector.get_columns("user")]

    if "pdf_parsing_preference" in columns:
        # Remove pdf_parsing_preference column from user table
        op.drop_column("user", "pdf_parsing_preference")
