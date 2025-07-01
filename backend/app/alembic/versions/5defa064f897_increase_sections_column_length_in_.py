"""increase_sections_column_length_in_reportgenie_outlines

Revision ID: 5defa064f897
Revises: bd29dc14440a
Create Date: 2025-06-30 22:51:05.589077

"""

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = "5defa064f897"
down_revision = "bd29dc14440a"
branch_labels = None
depends_on = None


def upgrade():
    # Change sections column from VARCHAR(255) to TEXT to allow longer section descriptions
    op.alter_column(
        "reportgenie_outlines",
        "sections",
        existing_type=sa.VARCHAR(length=255),
        type_=sa.TEXT(),
        existing_nullable=False,
    )


def downgrade():
    # Revert sections column back to VARCHAR(255) - WARNING: this may truncate data!
    op.alter_column(
        "reportgenie_outlines",
        "sections",
        existing_type=sa.TEXT(),
        type_=sa.VARCHAR(length=255),
        existing_nullable=False,
    )
