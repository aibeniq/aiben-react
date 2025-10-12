"""Add account lockout fields to user table

Revision ID: add_account_lockout
Revises: add_file_storage_fields
Create Date: 2025-10-12 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "add_account_lockout"
down_revision = "add_file_storage_fields"  # Point to the existing migration
branch_labels = None
depends_on = None


def upgrade():
    """Add failed_login_attempts and locked_until columns to user table."""
    op.add_column(
        "user",
        sa.Column(
            "failed_login_attempts",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )
    op.add_column(
        "user",
        sa.Column(
            "locked_until",
            sa.DateTime(),
            nullable=True,
        ),
    )


def downgrade():
    """Remove account lockout columns from user table."""
    op.drop_column("user", "locked_until")
    op.drop_column("user", "failed_login_attempts")
