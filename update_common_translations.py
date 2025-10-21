#!/usr/bin/env python3
"""
Script to add new translation keys to all language files.
"""

import os
import json
from pathlib import Path

# New keys to add to the ui section
NEW_KEYS = {
    "topicLabel": "[TODO] Topic:",
    "knowledgeBaseReference": "[TODO] Knowledge Base Reference",
    "knowledgeBaseReferences": "[TODO] Knowledge Base References",
    "hideReferences": "[TODO] Hide References",
    "showReferences": "[TODO] Show References",
    "referenceNumber": "[TODO] Reference {{number}}",
    "processedInChunks": "[TODO] Processed in {{count}} chunks",
    "synthesisError": "[TODO] Error synthesizing topic analysis",
}


def update_language_file(file_path):
    """Update a language file with new keys."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Ensure ui section exists
        if "ui" not in data:
            data["ui"] = {}

        # Add new keys if they don't exist
        for key, value in NEW_KEYS.items():
            if key not in data["ui"]:
                data["ui"][key] = value

        # Write back the updated file
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"Updated {file_path}")
        return True

    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False


def main():
    locales_dir = Path("frontend/src/locales")

    if not locales_dir.exists():
        print("Locales directory not found")
        return

    updated_count = 0

    # Process all language directories except 'en' and 'vi' (already done)
    for lang_dir in locales_dir.iterdir():
        if lang_dir.is_dir() and lang_dir.name not in ["en", "vi"]:
            common_file = lang_dir / "common.json"
            if common_file.exists():
                if update_language_file(common_file):
                    updated_count += 1

    print(f"Updated {updated_count} language files")


if __name__ == "__main__":
    main()
