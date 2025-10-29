"""Add pdf_parsing_preference to user

Revision ID: a1b2c3d4e5f7
Revises: 483afa1509d2
Create Date: 2025-10-29 12:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f7"
down_revision = "483afa1509d2"
branch_labels = None
depends_on = None


def upgrade() -> None:
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
    # Remove pdf_parsing_preference column from user table
    op.drop_column("user", "pdf_parsing_preference")
