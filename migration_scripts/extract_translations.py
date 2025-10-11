#!/usr/bin/env python3
"""
Extract translations from i18n.ts and create proper JSON files
"""

import json
import re
import os
from pathlib import Path

def extract_typescript_object(content, start_marker):
    """Extract a TypeScript object starting from a marker"""
    # Find the start of the object
    start_idx = content.find(start_marker)
    if start_idx == -1:
        return None
    
    # Find the opening brace
    brace_idx = content.find('{', start_idx)
    if brace_idx == -1:
        return None
    
    # Count braces to find matching closing brace
    depth = 0
    i = brace_idx
    while i < len(content):
        if content[i] == '{':
            depth += 1
        elif content[i] == '}':
            depth -= 1
            if depth == 0:
                return content[brace_idx:i+1]
        i += 1
    
    return None

def clean_typescript_to_json(ts_obj):
    """Convert TypeScript object syntax to JSON"""
    # Remove comments
    ts_obj = re.sub(r'//.*?$', '', ts_obj, flags=re.MULTILINE)
    ts_obj = re.sub(r'/\*.*?\*/', '', ts_obj, flags=re.DOTALL)
    
    # Convert unquoted keys to quoted keys
    ts_obj = re.sub(r'(\n\s*)(\w+):', r'\1"\2":', ts_obj)
    
    # Fix template literals - convert to regular strings
    ts_obj = re.sub(r'`([^`]*)`', lambda m: json.dumps(m.group(1)), ts_obj)
    
    # Handle multi-line strings (string concatenation)
    # Match patterns like: "text"\n  "more text"
    def join_multiline(match):
        # Get all the string parts
        parts = re.findall(r'"([^"]*)"', match.group(0))
        # Join with space and return as single JSON string
        return json.dumps(' '.join(parts))
    
    ts_obj = re.sub(r'"[^"]*"\s*\n\s*(?:"[^"]*"\s*\n\s*)*"[^"]*"', join_multiline, ts_obj)
    
    # Remove trailing commas before closing braces/brackets
    ts_obj = re.sub(r',(\s*[}\]])', r'\1', ts_obj)
    
    return ts_obj

def extract_language_block(content, lang_code):
    """Extract a specific language block from i18n.ts"""
    marker = f'resources.{lang_code} = {{'
    alt_marker = f'resources["{lang_code}"] = {{'
    
    block = extract_typescript_object(content, marker)
    if not block:
        block = extract_typescript_object(content, alt_marker)
    
    return block

def save_json_file(data, lang_code, output_dir):
    """Save translation data to JSON file"""
    lang_dir = output_dir / lang_code
    lang_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = lang_dir / 'common.json'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Saved {lang_code} to {output_file}")

def main():
    # Read the i18n.ts file
    i18n_path = Path(__file__).parent.parent / 'frontend' / 'src' / 'i18n.ts'
    
    with open(i18n_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Output directory
    output_dir = Path(__file__).parent.parent / 'frontend' / 'src' / 'locales'
    
    # Languages to extract from i18n.ts (inline definitions)
    inline_languages = [
        'en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 
        'zh', 'ja', 'uk', 'pl', 'nl', 'ko', 'ar', 'hi'
    ]
    
    for lang in inline_languages:
        print(f"🔍 Extracting {lang}...")
        
        # Extract the language block
        block = extract_language_block(content, lang)
        
        if block:
            try:
                # Clean and parse
                json_str = clean_typescript_to_json(block)
                
                # Parse JSON
                data = json.loads(json_str)
                
                # Extract just the 'common' part
                if 'common' in data:
                    save_json_file(data['common'], lang, output_dir)
                else:
                    save_json_file(data, lang, output_dir)
                    
            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse {lang}: {e}")
                # Save the cleaned string for debugging
                debug_file = output_dir / f'{lang}_debug.txt'
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(json_str)
                print(f"   Debug output saved to {debug_file}")
        else:
            print(f"⚠️  Could not find {lang} block")
    
    print(f"\n✨ Extraction complete! Check {output_dir}")

if __name__ == '__main__':
    main()
