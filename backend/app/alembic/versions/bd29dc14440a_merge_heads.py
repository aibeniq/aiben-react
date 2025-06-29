"""merge heads

Revision ID: bd29dc14440a
Revises: 4098fcfa636a, f1e2d3c4b5a6
Create Date: 2025-06-28 22:27:48.448522

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = 'bd29dc14440a'
down_revision = ('4098fcfa636a', 'f1e2d3c4b5a6')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
