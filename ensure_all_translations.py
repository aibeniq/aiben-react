#!/usr/bin/env python3
"""
Ensure all supported languages have all required translation keys.
Copies structure from English and marks missing translations with [TODO: ...].
"""

import json
import os
from pathlib import Path

# Required translation keys based on English structure
REQUIRED_KEYS = {
    "common.progress.starting": "Starting...",
    "common.progress.initializing": "Initializing...",
    "common.progress.processing": "Processing...",
    "common.progress.extracting": "Extracting content...",
    
    "generate.pleaseWait": "Please wait while we generate your report",
    "generate.progress.starting": "Starting...",
    "generate.progress.initializing": "Initializing...",
    "generate.progress.generating": "Generating report...",
    "generate.progress.processingSection": "Processing section {{sectionNum}} of {{totalSections}}: {{sectionPreview}}",
    
    "compare.pleaseWait": "Please wait while we compare your documents",
    "compare.progress.starting": "Starting...",
    "compare.progress.initializing": "Initializing...",
    "compare.progress.comparing": "Comparing...",
    "compare.compareSuccess": "Documents compared successfully!",
    
    "match.pleaseWait": "Please wait while we match your documents",
    "match.progress.starting": "Starting...",
    "match.progress.initializing": "Initializing...",
    "match.progress.formatting": "Comparing and formatting results...",
    "match.progress.matching": "Matching fields...",
    "match.matchSuccess": "Form processing completed successfully!",
    "match.singleDocumentSuccess": "Field values extracted from single document.",
    
    "review.pleaseWait": "Please wait while we review your documents",
}

def get_nested_value(data, key_path):
    """Get value from nested dict using dot notation."""
    keys = key_path.split('.')
    value = data
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return None
    return value

def set_nested_value(data, key_path, value):
    """Set value in nested dict using dot notation."""
    keys = key_path.split('.')
    current = data
    
    for i, key in enumerate(keys[:-1]):
        if key not in current:
            current[key] = {}
        current = current[key]
    
    current[keys[-1]] = value

def ensure_translation_keys(lang_code, lang_file_path):
    """Ensure all required keys exist in the language file."""
    print(f"\n{'='*60}")
    print(f"Processing: {lang_code}")
    print(f"{'='*60}")
    
    with open(lang_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    missing_keys = []
    updated = False
    
    for key_path, english_value in REQUIRED_KEYS.items():
        current_value = get_nested_value(data, key_path)
        
        if current_value is None:
            # Key is missing
            missing_keys.append(key_path)
            todo_value = f"[TODO: {english_value}]"
            set_nested_value(data, key_path, todo_value)
            print(f"  ✨ ADDED: {key_path} = {todo_value}")
            updated = True
        elif current_value == english_value and lang_code != 'en':
            # Value is still in English (not translated)
            todo_value = f"[TODO: {english_value}]"
            set_nested_value(data, key_path, todo_value)
            print(f"  🔄 MARKED: {key_path} = {todo_value} (was English)")
            updated = True
        elif current_value.startswith("[TODO:"):
            print(f"  ⏳ PENDING: {key_path} = {current_value}")
        else:
            print(f"  ✅ OK: {key_path}")
    
    if updated:
        with open(lang_file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"\n  💾 Updated {lang_code}/common.json")
    else:
        print(f"\n  ✓ No changes needed for {lang_code}")
    
    return len(missing_keys), updated

def main():
    locales_dir = Path(__file__).parent / "frontend" / "src" / "locales"
    
    print("Ensuring all translation keys are present in all languages...")
    print(f"Locales directory: {locales_dir}")
    
    # Get all language directories
    lang_dirs = [d for d in locales_dir.iterdir() if d.is_dir() and (d / "common.json").exists()]
    
    total_missing = 0
    total_updated = 0
    
    for lang_dir in sorted(lang_dirs):
        lang_code = lang_dir.name
        common_file = lang_dir / "common.json"
        
        missing, updated = ensure_translation_keys(lang_code, common_file)
        total_missing += missing
        if updated:
            total_updated += 1
    
    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"Total languages processed: {len(lang_dirs)}")
    print(f"Languages updated: {total_updated}")
    print(f"Total missing keys added: {total_missing}")
    print(f"\nAll files have been updated with missing keys marked as [TODO: ...]")
    print(f"Professional translation is recommended for production use.")

if __name__ == "__main__":
    main()
