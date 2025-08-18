#!/usr/bin/env python3
"""Generate OpenAPI spec for the API."""

import json
from backend.app.main import app

if __name__ == "__main__":
    openapi_schema = app.openapi()
    with open("backend/openapi.json", "w") as f:
        json.dump(openapi_schema, f, indent=2)
    print("OpenAPI spec generated successfully!")
