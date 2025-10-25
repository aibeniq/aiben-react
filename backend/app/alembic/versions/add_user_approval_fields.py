"""Add user approval fields

Revision ID: add_user_approval_fields
Revises: merge_lockout_and_storage
Create Date: 2025-10-24 12:00:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision = "add_user_approval_fields"
down_revision = "merge_lockout_and_storage"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop the status column if it exists (to avoid conflicts)
    op.drop_column("user", "status")

    # Drop enum type if it exists
    op.execute("DROP TYPE IF EXISTS userstatus CASCADE")

    # Add new columns without creating custom enum type
    # Let SQLAlchemy handle the enum
    op.add_column(
        "user",
        sa.Column(
            "status",
            sa.String(),
            nullable=True,
        ),
    )
    op.add_column("user", sa.Column("registration_date", sa.DateTime(), nullable=True))
    op.add_column("user", sa.Column("approved_date", sa.DateTime(), nullable=True))
    op.add_column(
        "user", sa.Column("approved_by", postgresql.UUID(as_uuid=True), nullable=True)
    )

    # Set existing users to 'active' status
    op.execute("UPDATE \"user\" SET status = 'active' WHERE status IS NULL")

    # Set registration_date for existing users to current timestamp
    op.execute(
        'UPDATE "user" SET registration_date = NOW() WHERE registration_date IS NULL'
    )

    # Make status NOT NULL after setting defaults
    op.alter_column("user", "status", nullable=False)
    op.alter_column("user", "registration_date", nullable=False)

    # Add foreign key constraint for approved_by
    op.create_foreign_key(
        "fk_user_approved_by",
        "user",
        "user",
        ["approved_by"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_user_approved_by", "user", type_="foreignkey")
    op.drop_column("user", "approved_by")
    op.drop_column("user", "approved_date")
    op.drop_column("user", "registration_date")
    op.drop_column("user", "status")
