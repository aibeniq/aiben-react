#!/usr/bin/env python3
"""Generate OpenAPI schema."""
import json
import app.main

with open("../openapi.json", "w", encoding="utf-8") as f:
    json.dump(app.main.app.openapi(), f, indent=2)

print("✓ OpenAPI schema generated")
