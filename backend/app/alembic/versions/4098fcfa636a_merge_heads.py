"""merge heads

Revision ID: 4098fcfa636a
Revises: 3161076ef46f, update_outline_sections_to_structured_format
Create Date: 2025-06-26 18:08:52.017899

"""

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = "4098fcfa636a"
down_revision = ("3161076ef46f", "b1a2c3d4e5f6")
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
