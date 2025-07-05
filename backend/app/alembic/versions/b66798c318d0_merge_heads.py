"""merge_heads

Revision ID: b66798c318d0
Revises: 7b94b6c142de
Create Date: 2025-07-04 18:11:11.235606

"""

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = "b66798c318d0"
down_revision = "7b94b6c142de"
branch_labels = None
depends_on = None


def upgrade():
    # Convert default_embedding_model from UUID to VARCHAR(100)
    # First, drop the foreign key constraint
    op.drop_constraint("user_default_embedding_model_fkey", "user", type_="foreignkey")

    # Add a temporary column with the string values
    op.add_column(
        "user",
        sa.Column("default_embedding_model_temp", sa.String(length=100), nullable=True),
    )

    # Populate the temporary column with the converted values
    op.execute(
        """
        UPDATE "user" 
        SET default_embedding_model_temp = (
            SELECT em.model_id 
            FROM embeddingmodel em 
            WHERE em.id = "user".default_embedding_model
        )
        WHERE default_embedding_model IS NOT NULL
        """
    )

    # Drop the original UUID column
    op.drop_column("user", "default_embedding_model")

    # Rename the temporary column to the original name
    op.alter_column(
        "user",
        "default_embedding_model_temp",
        new_column_name="default_embedding_model",
    )


def downgrade():
    # Convert back from VARCHAR to UUID
    # This is more complex as we'd need to reverse the lookup
    op.alter_column(
        "user",
        "default_embedding_model",
        existing_type=sa.String(length=100),
        type_=sa.UUID(),
        existing_nullable=True,
    )

    # Re-add the foreign key constraint
    op.create_foreign_key(
        "user_default_embedding_model_fkey",
        "user",
        "embeddingmodel",
        ["default_embedding_model"],
        ["id"],
    )
