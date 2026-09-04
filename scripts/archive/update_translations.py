#!/usr/bin/env python3
"""
Script to update all translation files with new welcome message keys
"""

import os
import re

# Define the translation files to update and their languages
translation_files = [
    {
        "file": "frontend/src/translations_central_european.ts",
        "languages": {
            "cs": {
                "welcomeBack": "Vítejte zpět, je hezké vás znovu vidět!",
                "hiUser": "Ahoj, {{name}} 👋",
            },  # Czech
            "sk": {
                "welcomeBack": "Vitajte späť, je pekné vás znovu vidieť!",
                "hiUser": "Ahoj, {{name}} 👋",
            },  # Slovak
            "hu": {
                "welcomeBack": "Isten hozott vissza, jó újra látni!",
                "hiUser": "Szia, {{name}} 👋",
            },  # Hungarian
            "ro": {
                "welcomeBack": "Bine ai revenit, mă bucur să te văd din nou!",
                "hiUser": "Salut, {{name}} 👋",
            },  # Romanian
            "bg": {
                "welcomeBack": "Добре дошли отново, приятно е да ви видя пак!",
                "hiUser": "Здравей, {{name}} 👋",
            },  # Bulgarian
            "hr": {
                "welcomeBack": "Dobrodošli natrag, lijepo vas je ponovno vidjeti!",
                "hiUser": "Bok, {{name}} 👋",
            },  # Croatian
            "sr": {
                "welcomeBack": "Добродошли назад, лепо је видети вас поново!",
                "hiUser": "Здраво, {{name}} 👋",
            },  # Serbian
            "sl": {
                "welcomeBack": "Dobrodošli nazaj, lepo vas je spet videti!",
                "hiUser": "Pozdrav, {{name}} 👋",
            },  # Slovenian
        },
    },
    {
        "file": "frontend/src/translations_baltic_eastern_european.ts",
        "languages": {
            "et": {
                "welcomeBack": "Tere tulemast tagasi, hea on sind jälle näha!",
                "hiUser": "Tere, {{name}} 👋",
            },  # Estonian
            "lv": {
                "welcomeBack": "Laipni lūdzam atpakaļ, prieks jūs atkal redzēt!",
                "hiUser": "Sveiki, {{name}} 👋",
            },  # Latvian
            "lt": {
                "welcomeBack": "Sveiki sugrįžę, malonu vėl jus matyti!",
                "hiUser": "Labas, {{name}} 👋",
            },  # Lithuanian
            "el": {
                "welcomeBack": "Καλώς ήρθατε πίσω, χαίρομαι που σας βλέπω ξανά!",
                "hiUser": "Γεια σας, {{name}} 👋",
            },  # Greek
        },
    },
    {
        "file": "frontend/src/translations_asian.ts",
        "languages": {
            "zh-TW": {
                "welcomeBack": "歡迎回來，很高興再次見到您！",
                "hiUser": "您好，{{name}} 👋",
            },  # Chinese Traditional
            "th": {
                "welcomeBack": "ยินดีต้อนรับกลับมา ดีใจที่ได้เจอกันอีกครั้ง!",
                "hiUser": "สวัสดี {{name}} 👋",
            },  # Thai
            "vi": {
                "welcomeBack": "Chào mừng trở lại, rất vui được gặp lại bạn!",
                "hiUser": "Xin chào, {{name}} 👋",
            },  # Vietnamese
            "id": {
                "welcomeBack": "Selamat datang kembali, senang melihat Anda lagi!",
                "hiUser": "Hai, {{name}} 👋",
            },  # Indonesian
            "ms": {
                "welcomeBack": "Selamat kembali, gembira melihat anda lagi!",
                "hiUser": "Hai, {{name}} 👋",
            },  # Malay
            "tl": {
                "welcomeBack": "Maligayang pagbabalik, natutuwa na makita ka ulit!",
                "hiUser": "Kumusta, {{name}} 👋",
            },  # Filipino
        },
    },
    {
        "file": "frontend/src/translations_middle_eastern_other.ts",
        "languages": {
            "he": {
                "welcomeBack": "ברוכים השבים, נחמד לראות אותך שוב!",
                "hiUser": "שלום, {{name}} 👋",
            },  # Hebrew
            "fa": {
                "welcomeBack": "خوش آمدید، خوشحالم که دوباره می‌بینمتان!",
                "hiUser": "سلام، {{name}} 👋",
            },  # Persian
            "tr": {
                "welcomeBack": "Tekrar hoş geldiniz, sizi yeniden görmek güzel!",
                "hiUser": "Merhaba, {{name}} 👋",
            },  # Turkish
            "sw": {
                "welcomeBack": "Karibu tena, ni furaha kukuona tena!",
                "hiUser": "Habari, {{name}} 👋",
            },  # Swahili
            "pt-BR": {
                "welcomeBack": "Bem-vindo de volta, bom te ver novamente!",
                "hiUser": "Oi, {{name}} 👋",
            },  # Portuguese Brazilian
            "es-LATAM": {
                "welcomeBack": "¡Bienvenido de vuelta, qué bueno verte de nuevo!",
                "hiUser": "Hola, {{name}} 👋",
            },  # Spanish Latin America
        },
    },
]


def update_translation_file(file_path, languages):
    """Update a single translation file with new welcome keys"""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    original_content = content

    for lang_code, translations in languages.items():
        # Pattern to find the common section for this language
        pattern = rf'(resources\.{re.escape(lang_code)}\s*=\s*\{{.*?common:\s*\{{[^}}]*welcome:\s*"[^"]*",)(.*?)(goodbye:)'

        def replacement(match):
            before_welcome = match.group(1)
            middle = match.group(2)
            after_goodbye = match.group(3)

            # Add the new keys after welcome
            new_keys = f'\n        welcomeBack: "{translations["welcomeBack"]}",\n        hiUser: "{translations["hiUser"]}",\n        '

            return before_welcome + new_keys + after_goodbye

        content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    if content != original_content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Updated: {file_path}")
    else:
        print(f"No changes made to: {file_path}")


def main():
    for file_info in translation_files:
        update_translation_file(file_info["file"], file_info["languages"])


if __name__ == "__main__":
    main()
