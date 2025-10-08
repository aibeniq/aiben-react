#!/usr/bin/env python3
"""
Script to add missing pleaseWait translations to all language files.
This adds the missing pleaseWait keys to review, match, and compare sections.
"""

import os
import re
from pathlib import Path

# Default fallback translations for pleaseWait messages
DEFAULT_TRANSLATIONS = {
    'review.pleaseWait': 'Please wait while we review your documents',
    'match.pleaseWait': 'Please wait while we process your documents', 
    'compare.pleaseWait': 'Please wait while we compare your documents'
}

def add_missing_pleasewait(file_path, language_code):
    """Add missing pleaseWait keys to a translation file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if review section exists and is missing pleaseWait
        review_pattern = r'(\s+fullScanDescription:\s*[^}]+?)(}\s*,?\s*$)'
        if 'review:' in content and 'fullScanDescription:' in content:
            if 'pleaseWait:' not in content.split('review:')[1].split('},')[0]:
                # Add pleaseWait to review section
                content = re.sub(
                    review_pattern,
                    r'\1        pleaseWait: "Please wait while we review your documents",\n      }',
                    content,
                    flags=re.MULTILINE | re.DOTALL
                )
        
        # Check match section
        if 'match:' in content and 'pleaseWait:' not in content.split('match:')[1].split('},')[0]:
            match_pattern = r'(match:\s*{[^}]*?pleaseWait:\s*"[^"]*")'
            if not re.search(match_pattern, content):
                # Find the match section and add pleaseWait
                match_section_pattern = r'(match:\s*{[^}]*?)(\s+}\s*,?\s*$)'
                content = re.sub(
                    match_section_pattern,
                    r'\1        pleaseWait: "Please wait while we process your documents",\n      }',
                    content,
                    flags=re.MULTILINE | re.DOTALL
                )
        
        # Check compare section  
        if 'compare:' in content and 'pleaseWait:' not in content.split('compare:')[1].split('},')[0]:
            compare_pattern = r'(compare:\s*{[^}]*?pleaseWait:\s*"[^"]*")'
            if not re.search(compare_pattern, content):
                # Find the compare section and add pleaseWait
                compare_section_pattern = r'(compare:\s*{[^}]*?)(\s+}\s*,?\s*$)'
                content = re.sub(
                    compare_section_pattern,
                    r'\1        pleaseWait: "Please wait while we compare your documents",\n      }',
                    content,
                    flags=re.MULTILINE | re.DOTALL
                )
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"Updated {file_path}")
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

def main():
    src_dir = Path('.')
    
    # Process i18n.ts
    i18n_file = src_dir / 'i18n.ts'
    if i18n_file.exists():
        add_missing_pleasewait(i18n_file, 'en')
    
    # Process translation files
    for file_path in src_dir.glob('translations_*.ts'):
        # Extract language code from filename
        filename = file_path.name
        if filename.startswith('translations_') and filename.endswith('.ts'):
            lang_part = filename[13:-3]  # Remove 'translations_' and '.ts'
            add_missing_pleasewait(file_path, lang_part)

if __name__ == '__main__':
    main()
