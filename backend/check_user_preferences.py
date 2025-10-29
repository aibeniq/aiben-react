#!/usr/bin/env python3
"""Check user's PDF parsing preference."""
from sqlalchemy import create_engine, text
from app.core.config import settings

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))

with engine.connect() as conn:
    result = conn.execute(
        text(
            'SELECT id, email, pdf_parsing_preference FROM "user" ORDER BY registration_date DESC LIMIT 5'
        )
    )

    print("\nRecent users and their PDF parsing preferences:")
    print("-" * 80)
    for row in result:
        print(f"ID: {row[0]}")
        print(f"Email: {row[1]}")
        print(f"PDF Parsing Preference: {row[2]}")
        print("-" * 80)
