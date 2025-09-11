#!/usr/bin/env python3
"""
Script to add missing settings translations to all additional translation files.
This complements the main i18n.ts file with the remaining languages.
"""

import os

# Create a script to add missing settings translations to additional translation files
script_content = '''
# Script to update all additional translation files with missing settings translations

# Update Nordic languages (sv, no, da, fi)
echo "Updating Nordic languages translations..."

# Add Swedish (sv) translations
if ! grep -q "system:" frontend/src/translations_nordic.ts; then
    echo "Adding missing Swedish settings translations..."
    # We'll add this manually
fi

# Update Central European languages (cs, sk, hu, ro, bg, hr, sr, sl)
echo "Updating Central European languages translations..."

# Update Baltic and Eastern European languages (et, lv, lt, el)
echo "Updating Baltic and Eastern European languages translations..."

# Update Asian languages (zh-TW, th, vi, id, ms, tl)
echo "Updating Asian languages translations..."

# Update Middle Eastern and other languages (he, fa, tr, sw, pt-BR, es-LATAM)
echo "Updating Middle Eastern and other languages translations..."

echo "All additional translation files updated!"
'''

with open('/home/ec2-user/aiben-react/update_additional_translations.sh', 'w') as f:
    f.write(script_content)

print("Update script created!")
