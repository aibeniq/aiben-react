"""Update outline sections to structured format

Revision ID: update_outline_sections_to_structured_format
Revises: 13558e98d29a
Create Date: 2025-06-26 20:00:00.000000

"""

from alembic import op
import sqlalchemy as sa
import json


# revision identifiers, used by Alembic.
revision = "b1a2c3d4e5f6"
down_revision = "13558e98d29a"
branch_labels = None
depends_on = None


def upgrade():
    """
    Convert existing string-based sections to structured JSON format
    """
    # Get connection
    connection = op.get_bind()

    # Query all existing outlines
    result = connection.execute(
        sa.text("SELECT id, sections FROM reportgenie_outlines")
    )

    for row in result:
        outline_id, sections_str = row

        # Skip if already in JSON format
        try:
            parsed = json.loads(sections_str)
            if isinstance(parsed, list) and all(
                isinstance(item, dict) and "text" in item and "consultDocuments" in item
                for item in parsed
            ):
                continue  # Already in new format
        except (json.JSONDecodeError, TypeError):
            pass

        # Convert string format to structured format
        if sections_str and isinstance(sections_str, str):
            # Split by newlines and create structured data
            section_lines = [
                line.strip() for line in sections_str.split("\n") if line.strip()
            ]
            structured_sections = []

            for line in section_lines:
                structured_sections.append(
                    {
                        "id": f"section-{len(structured_sections)}",  # Simple ID
                        "text": line,
                        "consultDocuments": True,  # Default to True for existing sections
                    }
                )

            # Update the database with the new structured format
            if structured_sections:
                new_sections_json = json.dumps(structured_sections)
                connection.execute(
                    sa.text(
                        "UPDATE reportgenie_outlines SET sections = :sections WHERE id = :id"
                    ),
                    {"sections": new_sections_json, "id": outline_id},
                )


def downgrade():
    """
    Convert structured JSON format back to string format
    """
    # Get connection
    connection = op.get_bind()

    # Query all existing outlines
    result = connection.execute(
        sa.text("SELECT id, sections FROM reportgenie_outlines")
    )

    for row in result:
        outline_id, sections_str = row

        # Try to parse as JSON
        try:
            sections_data = json.loads(sections_str)
            if isinstance(sections_data, list) and all(
                isinstance(item, dict) and "text" in item for item in sections_data
            ):
                # Convert back to string format
                section_lines = [
                    item["text"] for item in sections_data if item.get("text")
                ]
                new_sections_str = "\n".join(section_lines)

                # Update the database
                connection.execute(
                    sa.text(
                        "UPDATE reportgenie_outlines SET sections = :sections WHERE id = :id"
                    ),
                    {"sections": new_sections_str, "id": outline_id},
                )
        except (json.JSONDecodeError, TypeError):
            pass  # Already in string format or invalid data
