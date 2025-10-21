#!/usr/bin/env python3
"""
Verify that all locale files have progress keys correctly nested under knowledgeBases.
"""

import json
from pathlib import Path

LOCALES_DIR = Path("frontend/src/locales")

# Keys that should be in knowledgeBases.progress
KB_PROGRESS_KEYS = {
    "uploading",
    "saving_file",
    "processing_file",
    "processed_chunks",
    "processed_all_chunks",
    "chunking",
    "chunking_complete",
    "embedding",
    "embedding_complete",
    "storing",
    "storing_complete",
    "finalizing",
    "kb_creation_complete",
}


def check_locale_file(filepath):
    """Check if a locale file has correctly nested KB progress keys."""

    locale_name = filepath.parent.name

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Check if knowledgeBases.progress exists
    kb_progress = data.get("knowledgeBases", {}).get("progress", {})

    if not kb_progress:
        print(f"❌ {locale_name:10s} - NO knowledgeBases.progress section found!")
        return False

    # Check which KB progress keys are present
    found_keys = set(kb_progress.keys()) & KB_PROGRESS_KEYS
    missing_keys = KB_PROGRESS_KEYS - found_keys

    if len(found_keys) >= 10:  # Most keys present
        print(
            f"✅ {locale_name:10s} - Has {len(found_keys)}/{len(KB_PROGRESS_KEYS)} KB progress keys"
        )
        return True
    elif len(found_keys) > 0:
        print(
            f"⚠️  {locale_name:10s} - Has only {len(found_keys)}/{len(KB_PROGRESS_KEYS)} KB progress keys"
        )
        print(f"   Missing: {missing_keys}")
        return False
    else:
        print(
            f"❌ {locale_name:10s} - No KB progress keys found in knowledgeBases.progress"
        )
        return False


def main():
    """Check all locale files."""

    if not LOCALES_DIR.exists():
        print(f"Error: Locales directory not found: {LOCALES_DIR}")
        return

    locale_files = sorted(LOCALES_DIR.glob("*/common.json"))

    print(
        f"Checking {len(locale_files)} locale files for correct KB progress nesting...\n"
    )

    good_count = 0
    bad_count = 0

    for filepath in locale_files:
        if check_locale_file(filepath):
            good_count += 1
        else:
            bad_count += 1

    print(f"\n{'='*60}")
    print(f"Summary: {good_count} OK, {bad_count} Issues")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
