"""merge account lockout and file storage migrations

Revision ID: merge_lockout_and_storage
Revises: add_account_lockout, add_file_storage_fields
Create Date: 2025-10-12 04:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'merge_lockout_and_storage'
down_revision = ('add_account_lockout', 'add_file_storage_fields')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
