#!/usr/bin/env python3
"""
Update all translation files to change "Vector Search" to "Fast Search"
and "Full Document Scan" to "Deep Search"
"""

import json
import os
from pathlib import Path

# Base directory for locales
LOCALES_DIR = Path("frontend/src/locales")

# Mapping of old to new English terms
REPLACEMENTS = {
    "Vector Search": "Fast Search",
    "vector search": "fast search",
    "Full Document Scan": "Deep Search",
    "full document scan": "deep search",
    "Vector Search (Fast)": "Fast Search (Fast)",
    "Full Document Scan (Comprehensive)": "Deep Search (Comprehensive)",
}


def update_json_values(obj, replacements):
    """Recursively update JSON object values with replacements"""
    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, str):
                for old_text, new_text in replacements.items():
                    if old_text in value:
                        obj[key] = value.replace(old_text, new_text)
            elif isinstance(value, (dict, list)):
                update_json_values(value, replacements)
    elif isinstance(obj, list):
        for item in obj:
            update_json_values(item, replacements)
    return obj


def update_translation_file(file_path):
    """Update a single translation file"""
    print(f"Updating {file_path}...")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Update the data
        updated_data = update_json_values(data, REPLACEMENTS)

        # Write back
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(updated_data, f, ensure_ascii=False, indent=2)

        print(f"✓ Updated {file_path}")
        return True
    except Exception as e:
        print(f"✗ Error updating {file_path}: {e}")
        return False


def main():
    """Update all translation files"""
    if not LOCALES_DIR.exists():
        print(f"Error: {LOCALES_DIR} not found")
        return

    updated_count = 0
    error_count = 0

    # Find all common.json files
    for common_file in LOCALES_DIR.glob("*/common.json"):
        if update_translation_file(common_file):
            updated_count += 1
        else:
            error_count += 1

    print(f"\n{'='*60}")
    print(f"Summary: Updated {updated_count} files")
    if error_count > 0:
        print(f"Errors: {error_count} files failed")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
