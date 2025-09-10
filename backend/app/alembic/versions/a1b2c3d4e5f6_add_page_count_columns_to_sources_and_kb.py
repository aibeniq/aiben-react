"""Add page count columns to sources and knowledge bases

Revision ID: a1b2c3d4e5f6
Revises: f1e2d3c4b5a6
Create Date: 2025-09-10 19:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = 'f1e2d3c4b5a6'
branch_labels = None
depends_on = None


def upgrade():
    # Add page_count to sources table
    op.add_column('sources', sa.Column('page_count', sa.Integer(), nullable=False, server_default='0'))
    
    # Add total_pages to knowledge-bases table
    op.add_column('knowledge-bases', sa.Column('total_pages', sa.Integer(), nullable=False, server_default='0'))
    
    # Add indexes for performance
    op.create_index('idx_sources_page_count', 'sources', ['page_count'])
    op.create_index('idx_knowledge_bases_total_pages', 'knowledge-bases', ['total_pages'])


def downgrade():
    # Drop indexes
    op.drop_index('idx_knowledge_bases_total_pages', 'knowledge-bases')
    op.drop_index('idx_sources_page_count', 'sources')
    
    # Drop columns
    op.drop_column('knowledge-bases', 'total_pages')
    op.drop_column('sources', 'page_count')
