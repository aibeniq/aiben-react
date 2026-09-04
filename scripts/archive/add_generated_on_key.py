#!/usr/bin/env python3
"""
Add generatedOn key to docxHeaders in all common.json files.
"""

import json
import os
from pathlib import Path


def add_generated_on_to_common_json(lang_file_path):
    """Add the generatedOn key to docxHeaders in a common.json file."""
    with open(lang_file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "archive" not in data:
        data["archive"] = {}

    archive = data["archive"]

    if "docxHeaders" not in archive:
        archive["docxHeaders"] = {}

    docx_headers = archive["docxHeaders"]

    # Add the key if it doesn't exist
    if "generatedOn" not in docx_headers:
        docx_headers["generatedOn"] = (
            "[TODO: Generated on: {date} by user {name} - email: {email}]"
        )

    with open(lang_file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    locales_dir = Path("frontend/src/locales")
    if not locales_dir.exists():
        print("Locales directory not found")
        return

    lang_dirs = [
        d for d in locales_dir.iterdir() if d.is_dir() and (d / "common.json").exists()
    ]

    for lang_dir in lang_dirs:
        common_file = lang_dir / "common.json"
        print(f"Updating {lang_dir.name}/common.json")
        add_generated_on_to_common_json(common_file)

    print("All common.json files have been updated with generatedOn key.")


if __name__ == "__main__":
    main()
