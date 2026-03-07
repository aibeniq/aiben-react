"""Add team models and team membership

Revision ID: a3b4c5d6e7f8
Revises: 483afa1509d2
Create Date: 2026-03-07 10:00:00.000000

"""

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from sqlalchemy.dialects import postgresql
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision = "a3b4c5d6e7f8"
down_revision = "483afa1509d2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    
    # Create TeamRole enum type
    teamrole_enum = postgresql.ENUM('owner', 'admin', 'member', 'viewer', name='teamrole')
    teamrole_enum.create(conn, checkfirst=True)
    
    # Create teams table
    if 'teams' not in inspector.get_table_names():
        op.create_table(
            'teams',
            sa.Column('id', sa.UUID(), nullable=False),
            sa.Column('name', sa.String(length=255), nullable=False),
            sa.Column('description', sa.String(length=1000), nullable=True),
            sa.Column('created_by', sa.UUID(), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=False),
            sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
            sa.Column('deleted_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['created_by'], ['user.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('ix_teams_name', 'teams', ['name'], unique=True)
    
    # Create team_memberships table
    if 'team_memberships' not in inspector.get_table_names():
        op.create_table(
            'team_memberships',
            sa.Column('id', sa.UUID(), nullable=False),
            sa.Column('team_id', sa.UUID(), nullable=False),
            sa.Column('user_id', sa.UUID(), nullable=False),
            sa.Column('role', teamrole_enum, nullable=False, server_default='member'),
            sa.Column('joined_at', sa.DateTime(), nullable=False),
            sa.Column('added_by', sa.UUID(), nullable=True),
            sa.ForeignKeyConstraint(['added_by'], ['user.id'], ),
            sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('team_id', 'user_id', name='uq_team_user')
        )
    
    # Add current_team_id to user table
    columns = [col["name"] for col in inspector.get_columns("user")]
    if "current_team_id" not in columns:
        op.add_column(
            'user',
            sa.Column('current_team_id', sa.UUID(), nullable=True)
        )
        op.create_foreign_key(
            'fk_user_current_team_id_teams',
            'user', 'teams',
            ['current_team_id'], ['id']
        )


def downgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    
    # Drop current_team_id from user table
    columns = [col["name"] for col in inspector.get_columns("user")]
    if "current_team_id" in columns:
        op.drop_constraint('fk_user_current_team_id_teams', 'user', type_='foreignkey')
        op.drop_column('user', 'current_team_id')
    
    # Drop team_memberships table
    if 'team_memberships' in inspector.get_table_names():
        op.drop_table('team_memberships')
    
    # Drop teams table
    if 'teams' in inspector.get_table_names():
        op.drop_index('ix_teams_name', 'teams')
        op.drop_table('teams')
    
    # Drop TeamRole enum type
    teamrole_enum = postgresql.ENUM('owner', 'admin', 'member', 'viewer', name='teamrole')
    teamrole_enum.drop(conn, checkfirst=True)
