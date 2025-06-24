"""merge multiple heads

Revision ID: 3161076ef46f
Revises: 5621ccf38147, add_preferred_language
Create Date: 2025-06-24 10:45:24.797974

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = '3161076ef46f'
down_revision = ('5621ccf38147', 'add_preferred_language')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
