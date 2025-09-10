"""merge heads

Revision ID: e6ed8cd1320e
Revises: 6fc06b555c26, a1b2c3d4e5f6
Create Date: 2025-09-10 22:22:06.090078

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = 'e6ed8cd1320e'
down_revision = ('6fc06b555c26', 'a1b2c3d4e5f6')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
