"""Add vision_analysis_enabled to user

Revision ID: add_vision_analysis_enabled
Revises: merge_lockout_and_storage
Create Date: 2025-10-29 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "add_vision_analysis_enabled"
down_revision = "merge_lockout_and_storage"
branch_labels = None
depends_on = None


def upgrade():
    # Add vision_analysis_enabled column with default False for cost control
    op.add_column(
        "user",
        sa.Column(
            "vision_analysis_enabled",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
    )


def downgrade():
    op.drop_column("user", "vision_analysis_enabled")
