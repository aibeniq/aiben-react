"""Add preferred language to user

Revision ID: add_preferred_language
Revises: b7749e208d21
Create Date: 2023-07-01 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlmodel import SQLModel


# revision identifiers, used by Alembic.
revision = "add_preferred_language"
down_revision = "b7749e208d21"  # Change this to match the latest revision
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "user",
        sa.Column(
            "preferred_language",
            sa.String(length=10),
            nullable=False,
            server_default="en",
        ),
    )


def downgrade():
    op.drop_column("user", "preferred_language")
