"""Increase description length in VeraDoc checklist from 255 to 20000 characters

Revision ID: f1e2d3c4b5a6
Revises: b1a2c3d4e5f6
Create Date: 2025-06-28 23:40:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f1e2d3c4b5a6"
down_revision = "b1a2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Increase the length of the description column in the questions table
    op.alter_column(
        "questions",
        "description",
        existing_type=sa.VARCHAR(length=255),
        type_=sa.VARCHAR(length=20000),
        existing_nullable=True,
    )


def downgrade() -> None:
    # Revert the change back to 255 characters
    op.alter_column(
        "questions",
        "description",
        existing_type=sa.VARCHAR(length=20000),
        type_=sa.VARCHAR(length=255),
        existing_nullable=True,
    )
