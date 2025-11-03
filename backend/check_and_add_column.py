#!/usr/bin/env python3
"""
Check if pdf_parsing_preference column exists and add it if missing.
"""
from sqlalchemy import create_engine, text
from app.core.config import settings


def main():
    engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))

    with engine.connect() as conn:
        # Check if column exists
        result = conn.execute(
            text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name='user' AND column_name='pdf_parsing_preference'"
            )
        )

        if result.fetchone():
            print("✓ Column 'pdf_parsing_preference' already exists")
        else:
            print("Adding column 'pdf_parsing_preference'...")
            conn.execute(
                text(
                    "ALTER TABLE \"user\" ADD COLUMN pdf_parsing_preference VARCHAR(20) NOT NULL DEFAULT 'basic'"
                )
            )
            conn.commit()
            print("✓ Column added successfully")

        # Update alembic version
        result = conn.execute(text("SELECT version_num FROM alembic_version"))
        current_version = result.fetchone()[0]
        print(f"Current alembic version: {current_version}")

        if current_version == "8db31916c69b":
            print("Updating alembic version to 483afa1509d2...")
            conn.execute(
                text("UPDATE alembic_version SET version_num = '483afa1509d2'")
            )
            conn.commit()
            print("✓ Alembic version updated")


if __name__ == "__main__":
    main()
