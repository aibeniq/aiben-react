#!/usr/bin/env python3
"""
Script to add usage translations for knowledgeBasePages and pagesCount to all language files.
"""

import re
import os

# Language-specific translations
TRANSLATIONS = {
    # Chinese Simplified (already in main file)
    "zh": {
        "knowledgeBasePages": "知识库页面",
        "pagesCount": "页面"
    },
    # Chinese Traditional
    "zh-TW": {
        "knowledgeBasePages": "知識庫頁面",
        "pagesCount": "頁面"
    },
    # Japanese (already in main file)
    "ja": {
        "knowledgeBasePages": "ナレッジベースページ",
        "pagesCount": "ページ"
    },
    # Korean (already in main file)
    "ko": {
        "knowledgeBasePages": "지식 베이스 페이지",
        "pagesCount": "페이지"
    },
    # Ukrainian (already in main file)
    "uk": {
        "knowledgeBasePages": "Сторінки Бази Знань",
        "pagesCount": "сторінок"
    },
    # Polish (already in main file)
    "pl": {
        "knowledgeBasePages": "Strony Baz Wiedzy",
        "pagesCount": "stron"
    },
    # Dutch (already in main file)
    "nl": {
        "knowledgeBasePages": "Kennisbank Pagina's",
        "pagesCount": "pagina's"
    },
    # Arabic (already in main file)
    "ar": {
        "knowledgeBasePages": "صفحات قواعد المعرفة",
        "pagesCount": "صفحات"
    },
    # Hindi (already in main file)
    "hi": {
        "knowledgeBasePages": "ज्ञान आधार पृष्ठ",
        "pagesCount": "पृष्ठ"
    },
    # Nordic languages
    "sv": {
        "knowledgeBasePages": "Kunskapsbas Sidor",
        "pagesCount": "sidor"
    },
    "no": {
        "knowledgeBasePages": "Kunnskapsbase Sider",
        "pagesCount": "sider"
    },
    "da": {
        "knowledgeBasePages": "Vidensbase Sider",
        "pagesCount": "sider"
    },
    "fi": {
        "knowledgeBasePages": "Tietopohja Sivut",
        "pagesCount": "sivua"
    },
    # Central European languages
    "cs": {
        "knowledgeBasePages": "Stránky Znalostních Bází",
        "pagesCount": "stránek"
    },
    "sk": {
        "knowledgeBasePages": "Stránky Znalostných Báz",
        "pagesCount": "stránok"
    },
    "hu": {
        "knowledgeBasePages": "Tudásbázis Oldalak",
        "pagesCount": "oldal"
    },
    "ro": {
        "knowledgeBasePages": "Pagini Baze de Cunoștințe",
        "pagesCount": "pagini"
    },
    "bg": {
        "knowledgeBasePages": "Страници на Бази от Знания",
        "pagesCount": "страници"
    },
    "hr": {
        "knowledgeBasePages": "Stranice Baza Znanja",
        "pagesCount": "stranica"
    },
    "sr": {
        "knowledgeBasePages": "Странице База Знања",
        "pagesCount": "страница"
    },
    "sl": {
        "knowledgeBasePages": "Strani Baz Znanja",
        "pagesCount": "strani"
    },
    # Baltic and Eastern European
    "et": {
        "knowledgeBasePages": "Teadmusbaasi Leheküljed",
        "pagesCount": "lehekülge"
    },
    "lv": {
        "knowledgeBasePages": "Zināšanu Bāzes Lapas",
        "pagesCount": "lapas"
    },
    "lt": {
        "knowledgeBasePages": "Žinių Bazės Puslapiai",
        "pagesCount": "puslapių"
    },
    "el": {
        "knowledgeBasePages": "Σελίδες Βάσης Γνώσεων",
        "pagesCount": "σελίδες"
    },
    # Asian languages
    "th": {
        "knowledgeBasePages": "หน้าฐานความรู้",
        "pagesCount": "หน้า"
    },
    "vi": {
        "knowledgeBasePages": "Trang Cơ Sở Tri Thức",
        "pagesCount": "trang"
    },
    "id": {
        "knowledgeBasePages": "Halaman Basis Pengetahuan",
        "pagesCount": "halaman"
    },
    "ms": {
        "knowledgeBasePages": "Halaman Pangkalan Pengetahuan",
        "pagesCount": "halaman"
    },
    "tl": {
        "knowledgeBasePages": "Mga Pahina ng Base ng Kaalaman",
        "pagesCount": "mga pahina"
    },
    # Middle Eastern and other
    "he": {
        "knowledgeBasePages": "דפי בסיס הידע",
        "pagesCount": "דפים"
    },
    "fa": {
        "knowledgeBasePages": "صفحات پایگاه دانش",
        "pagesCount": "صفحات"
    },
    "tr": {
        "knowledgeBasePages": "Bilgi Tabanı Sayfaları",
        "pagesCount": "sayfa"
    },
    "sw": {
        "knowledgeBasePages": "Kurasa za Msingi wa Maarifa",
        "pagesCount": "kurasa"
    },
    "pt-BR": {
        "knowledgeBasePages": "Páginas de Bases de Conhecimento",
        "pagesCount": "páginas"
    },
    "es-LATAM": {
        "knowledgeBasePages": "Páginas de Bases de Conocimiento",
        "pagesCount": "páginas"
    }
}

def update_main_i18n_file():
    """Update the main i18n.ts file with remaining languages."""
    file_path = "/home/ec2-user/aiben-react/frontend/src/i18n.ts"
    
    # Languages that are in the main file and need updates
    main_file_languages = {
        "zh": {
            "knowledgeBasePages": "知识库页面",
            "pagesCount": "页面"
        },
        "ja": {
            "knowledgeBasePages": "ナレッジベースページ",
            "pagesCount": "ページ"
        },
        "uk": {
            "knowledgeBasePages": "Сторінки Бази Знань",
            "pagesCount": "сторінок"
        },
        "pl": {
            "knowledgeBasePages": "Strony Baz Wiedzy",
            "pagesCount": "stron"
        },
        "nl": {
            "knowledgeBasePages": "Kennisbank Pagina's",
            "pagesCount": "pagina's"
        },
        "ko": {
            "knowledgeBasePages": "지식 베이스 페이지",
            "pagesCount": "페이지"
        },
        "ar": {
            "knowledgeBasePages": "صفحات قواعد المعرفة",
            "pagesCount": "صفحات"
        },
        "hi": {
            "knowledgeBasePages": "ज्ञान आधार पृष्ठ",
            "pagesCount": "पृष्ठ"
        }
    }
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update each language section in the main file
    for lang_code, translations in main_file_languages.items():
        # Find the usage section for this language
        pattern = rf'({lang_code}.*?usage:\s*\{{[^}}]*?)(\}},)'
        
        def replace_usage(match):
            usage_section = match.group(1)
            closing = match.group(2)
            
            # Check if knowledgeBasePages already exists
            if 'knowledgeBasePages:' not in usage_section:
                # Add the new translations before the closing brace
                new_translations = f',\n        knowledgeBasePages: "{translations["knowledgeBasePages"]}",\n        pagesCount: "{translations["pagesCount"]}",'
                # Insert before the last line of the usage section
                lines = usage_section.split('\n')
                # Insert before the last line that should be the closing of usage
                lines.insert(-1, f'        knowledgeBasePages: "{translations["knowledgeBasePages"]}",')
                lines.insert(-1, f'        pagesCount: "{translations["pagesCount"]}",')
                usage_section = '\n'.join(lines)
            
            return usage_section + closing
        
        content = re.sub(pattern, replace_usage, content, flags=re.DOTALL)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Updated main i18n.ts file")

def update_additional_translation_files():
    """Update all additional translation files."""
    translation_files = [
        ("frontend/src/translations_nordic.ts", ["sv", "no", "da", "fi"]),
        ("frontend/src/translations_central_european.ts", ["cs", "sk", "hu", "ro", "bg", "hr", "sr", "sl"]),
        ("frontend/src/translations_baltic_eastern_european.ts", ["et", "lv", "lt", "el"]),
        ("frontend/src/translations_asian.ts", ["zh-TW", "th", "vi", "id", "ms", "tl"]),
        ("frontend/src/translations_middle_eastern_other.ts", ["he", "fa", "tr", "sw", "pt-BR", "es-LATAM"])
    ]
    
    for file_path, lang_codes in translation_files:
        full_path = f"/home/ec2-user/aiben-react/{file_path}"
        
        if not os.path.exists(full_path):
            print(f"File {full_path} does not exist, skipping...")
            continue
        
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Update each language in this file
        for lang_code in lang_codes:
            if lang_code not in TRANSLATIONS:
                continue
            
            translations = TRANSLATIONS[lang_code]
            
            # Find the usage section for this language and add the new translations
            pattern = rf'({lang_code}.*?usage:\s*\{{[^}}]*?)(\}},)'
            
            def replace_usage(match):
                usage_section = match.group(1)
                closing = match.group(2)
                
                # Check if knowledgeBasePages already exists
                if 'knowledgeBasePages:' not in usage_section:
                    # Add the new translations before the closing brace
                    lines = usage_section.split('\n')
                    # Find the line with usedOfQuota and add after it
                    for i, line in enumerate(lines):
                        if 'usedOfQuota:' in line:
                            lines.insert(i + 1, f'        knowledgeBasePages: "{translations["knowledgeBasePages"]}",')
                            lines.insert(i + 2, f'        pagesCount: "{translations["pagesCount"]}",')
                            break
                    usage_section = '\n'.join(lines)
                
                return usage_section + closing
            
            content = re.sub(pattern, replace_usage, content, flags=re.DOTALL)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Updated {file_path}")

if __name__ == "__main__":
    print("Adding usage translations to all language files...")
    update_main_i18n_file()
    update_additional_translation_files()
    print("All translation files updated!")
