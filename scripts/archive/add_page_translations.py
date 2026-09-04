#!/usr/bin/env python3
"""
Script to add knowledgeBaseTablePages translation to all language sections in i18n.ts
that are missing this key.
"""

import re

# Read the current i18n.ts file
with open('/home/ec2-user/aiben-react/frontend/src/i18n.ts', 'r', encoding='utf-8') as f:
    content = f.read()

# Language translations for "Pages"
translations = {
    'en': 'Pages',
    'es': 'Páginas', 
    'fr': 'Pages',
    'de': 'Seiten',
    'it': 'Pagine',
    'pt': 'Páginas',
    'ru': 'Страницы',
    'zh': '页面',
    'ja': 'ページ',
    'uk': 'Сторінки',
    'pl': 'Strony',
    'nl': 'Pagina\'s',
    'ko': '페이지',
    'ar': 'الصفحات',
    'hi': 'पृष्ठ'
}

# Pattern to find knowledgeBaseTableSources followed by selectKnowledgeBasePlaceholder
# This indicates we need to add knowledgeBaseTablePages between them
pattern = r'(\s+knowledgeBaseTableSources:\s*"[^"]+",)\s*(\s+selectKnowledgeBasePlaceholder:)'

def replacement_func(match):
    sources_line = match.group(1)
    placeholder_line = match.group(2)
    
    # Extract the language code by finding the nearest resources.xx = { line before this match
    # Search backwards from the match position to find the language definition
    text_before = content[:match.start()]
    lang_match = re.findall(r'resources\.([a-z]{2})\s*=\s*{', text_before)
    
    if lang_match:
        lang_code = lang_match[-1]  # Get the most recent language code
        if lang_code in translations:
            pages_translation = translations[lang_code]
            # Add the knowledgeBaseTablePages line with proper indentation
            indentation = "        "  # Match the existing indentation
            pages_line = f'{indentation}knowledgeBaseTablePages: "{pages_translation}",'
            return f'{sources_line}\n{pages_line}\n{placeholder_line}'
    
    # If we can't determine the language, don't modify
    return match.group(0)

# Apply the replacement
new_content = re.sub(pattern, replacement_func, content)

# Write the updated content back to the file
with open('/home/ec2-user/aiben-react/frontend/src/i18n.ts', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Translation update completed!")

# Show what languages were processed
processed_langs = re.findall(r'knowledgeBaseTablePages:\s*"([^"]+)"', new_content)
print(f"Added {len(processed_langs)} page translations")
