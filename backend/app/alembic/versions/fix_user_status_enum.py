"""Fix user status enum to use lowercase values

Revision ID: fix_user_status_enum
Revises: add_user_approval_fields
Create Date: 2025-10-25 12:00:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "fix_user_status_enum"
down_revision = "add_user_approval_fields"
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Check if the status column already has the correct enum values
    # This migration is a no-op if the enum is already correct
    
    # Step 1: Check if userstatus type exists and what values it has
    result = op.get_bind().execute(sa.text("""
        SELECT EXISTS (
            SELECT 1 FROM pg_type WHERE typname = 'userstatus'
        )
    """))
    type_exists = result.scalar()
    
    if not type_exists:
        # The type doesn't exist, which means add_user_approval_fields migration
        # hasn't run yet or failed. Skip this migration.
        return
    
    # Step 2: Add a temporary column with the correct enum type
    op.execute("CREATE TYPE userstatus_new AS ENUM ('pending', 'active', 'rejected', 'suspended')")
    
    op.add_column(
        "user",
        sa.Column("status_new", postgresql.ENUM('pending', 'active', 'rejected', 'suspended', name='userstatus_new'), nullable=True)
    )
    
    # Step 3: Copy data from old column to new column (lowercase values)
    # Map any existing values to lowercase equivalents
    op.execute("""
        UPDATE "user" 
        SET status_new = CASE 
            WHEN status::text = 'ACTIVE' THEN 'active'::userstatus_new
            WHEN status::text = 'PENDING' THEN 'pending'::userstatus_new
            WHEN status::text = 'REJECTED' THEN 'rejected'::userstatus_new
            WHEN status::text = 'SUSPENDED' THEN 'suspended'::userstatus_new
            WHEN status::text = 'active' THEN 'active'::userstatus_new
            WHEN status::text = 'pending' THEN 'pending'::userstatus_new
            WHEN status::text = 'rejected' THEN 'rejected'::userstatus_new
            WHEN status::text = 'suspended' THEN 'suspended'::userstatus_new
            ELSE 'active'::userstatus_new
        END
    """)
    
    # Step 4: Drop the old column and enum type
    op.drop_column("user", "status")
    op.execute("DROP TYPE IF EXISTS userstatus")
    
    # Step 5: Rename the new column and enum type
    op.alter_column("user", "status_new", new_column_name="status")
    op.execute("ALTER TYPE userstatus_new RENAME TO userstatus")
    
    # Step 6: Make the column NOT NULL
    op.alter_column("user", "status", nullable=False)

def downgrade() -> None:
    # Check if we need to downgrade
    result = op.get_bind().execute(sa.text("""
        SELECT EXISTS (
            SELECT 1 FROM pg_type WHERE typname = 'userstatus'
        )
    """))
    type_exists = result.scalar()
    
    if not type_exists:
        return
    
    # Reverse the process
    op.execute("CREATE TYPE userstatus_old AS ENUM ('PENDING', 'ACTIVE', 'REJECTED', 'SUSPENDED')")
    
    op.add_column(
        "user",
        sa.Column("status_old", postgresql.ENUM('PENDING', 'ACTIVE', 'REJECTED', 'SUSPENDED', name='userstatus_old'), nullable=True)
    )
    
    op.execute("""
        UPDATE "user" 
        SET status_old = CASE 
            WHEN status::text = 'active' THEN 'ACTIVE'::userstatus_old
            WHEN status::text = 'pending' THEN 'PENDING'::userstatus_old
            WHEN status::text = 'rejected' THEN 'REJECTED'::userstatus_old
            WHEN status::text = 'suspended' THEN 'SUSPENDED'::userstatus_old
        END
    """)
    
    op.drop_column("user", "status")
    op.execute("DROP TYPE IF EXISTS userstatus")
    
    op.alter_column("user", "status_old", new_column_name="status")
    op.execute("ALTER TYPE userstatus_old RENAME TO userstatus")
    
    op.alter_column("user", "status", nullable=False)
    op.alter_column("user", "status", nullable=False)