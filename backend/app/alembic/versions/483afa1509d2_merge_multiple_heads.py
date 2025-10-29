"""merge multiple heads

Revision ID: 483afa1509d2
Revises: add_vision_analysis_enabled, fix_user_status_enum
Create Date: 2025-10-29 11:02:05.704455

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = '483afa1509d2'
down_revision = ('add_vision_analysis_enabled', 'fix_user_status_enum')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
