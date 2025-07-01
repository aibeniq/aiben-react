"""increase_description_length_in_reportgenie_outlines

Revision ID: 6fc06b555c26
Revises: 5defa064f897
Create Date: 2025-06-30 22:56:30.027135

"""

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = "6fc06b555c26"
down_revision = "5defa064f897"
branch_labels = None
depends_on = None


def upgrade():
    # Change description column from VARCHAR(255) to TEXT to allow longer descriptions
    op.alter_column(
        "reportgenie_outlines",
        "description",
        existing_type=sa.VARCHAR(length=255),
        type_=sa.TEXT(),
        existing_nullable=True,
    )


def downgrade():
    # Revert description column back to VARCHAR(255) - WARNING: this may truncate data!
    op.alter_column(
        "reportgenie_outlines",
        "description",
        existing_type=sa.TEXT(),
        type_=sa.VARCHAR(length=255),
        existing_nullable=True,
    )
