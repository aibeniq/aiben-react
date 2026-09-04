#!/usr/bin/env python3
"""
Fix the nesting of progress keys in locale files.
The progress keys for knowledge base creation should be nested under knowledgeBases, not at the root level.
"""

import json
import os
from pathlib import Path

# Define the root locales directory
LOCALES_DIR = Path("frontend/src/locales")

# Keys that should be in knowledgeBases.progress
KB_PROGRESS_KEYS = {
    "uploading",
    "processingFile",
    "chunking",
    "embedding",
    "storing",
    "finalizing",
    "saving_file",
    "processing_file",
    "processed_chunks",
    "processed_all_chunks",
    "chunking_complete",
    "embedding_complete",
    "storing_complete",
    "kb_creation_complete",
}


def fix_locale_file(filepath):
    """Fix a single locale file by moving KB progress keys into knowledgeBases."""

    print(f"\nProcessing: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Check if there's a misplaced progress section
    if "progress" not in data:
        print(f"  ✓ No root-level progress section found")
        return False

    root_progress = data.get("progress", {})

    # Check if any KB progress keys are at root level
    kb_keys_at_root = set(root_progress.keys()) & KB_PROGRESS_KEYS

    if not kb_keys_at_root:
        print(f"  ✓ No KB progress keys at root level")
        return False

    print(
        f"  ⚠ Found {len(kb_keys_at_root)} KB progress keys at root level: {kb_keys_at_root}"
    )

    # Ensure knowledgeBases section exists
    if "knowledgeBases" not in data:
        print(f"  ✗ No knowledgeBases section found, cannot fix")
        return False

    # Ensure knowledgeBases.progress exists
    if "progress" not in data["knowledgeBases"]:
        data["knowledgeBases"]["progress"] = {}
        print(f"  + Created knowledgeBases.progress section")

    # Move KB progress keys from root to knowledgeBases
    moved_count = 0
    for key in kb_keys_at_root:
        data["knowledgeBases"]["progress"][key] = root_progress[key]
        del data["progress"][key]
        moved_count += 1

    print(f"  ✓ Moved {moved_count} keys to knowledgeBases.progress")

    # If root progress section is now empty, remove it
    # BUT keep it if it has other keys (like starting, initializing, etc.)
    if not data["progress"]:
        del data["progress"]
        print(f"  ✓ Removed empty root progress section")
    else:
        print(f"  ℹ Kept root progress section with {len(data['progress'])} other keys")

    # Write back the fixed data
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"  ✓ File updated successfully")
    return True


def main():
    """Process all locale files."""

    if not LOCALES_DIR.exists():
        print(f"Error: Locales directory not found: {LOCALES_DIR}")
        return

    # Find all common.json files
    locale_files = list(LOCALES_DIR.glob("*/common.json"))

    print(f"Found {len(locale_files)} locale files to process")

    fixed_count = 0
    for filepath in sorted(locale_files):
        if fix_locale_file(filepath):
            fixed_count += 1

    print(f"\n{'='*60}")
    print(f"Summary: Fixed {fixed_count} out of {len(locale_files)} files")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
