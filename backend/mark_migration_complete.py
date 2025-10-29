#!/usr/bin/env python3
"""Mark migration as complete."""
from sqlalchemy import create_engine, text
from app.core.config import settings

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
conn = engine.connect()
conn.execute(text("UPDATE alembic_version SET version_num = 'a1b2c3d4e5f7'"))
conn.commit()
print("✓ Migration marked as complete")
