import json
import os
from pathlib import Path

# Define the new keys to add
new_keys = {
    "question": {
        "en": "Question",
        "es": "Pregunta",
        "fr": "Question",
        "de": "Frage",
        "it": "Domanda",
        "pt": "Pergunta",
        "ru": "Вопрос",
        "zh": "问题",
        "ja": "質問",
        "ko": "질문",
        "nl": "Vraag",
        "pl": "Pytanie",
        "sv": "Fråga",
        "tr": "Soru",
        "uk": "Питання",
        "vi": "Câu hỏi",
        "ar": "سؤال",
        "bg": "Въпрос",
        "cs": "Otázka",
        "da": "Spørgsmål",
        "el": "Ερώτηση",
        "fa": "سوال",
        "he": "שאלה",
        "hi": "प्रश्न",
        "hr": "Pitanje",
        "hu": "Kérdés",
        "id": "Pertanyaan",
        "lt": "Klausimas",
        "lv": "Jautājums",
        "ms": "Soalan",
        "no": "Spørsmål",
        "ro": "Întrebare",
        "sk": "Otázka",
        "sl": "Vprašanje",
        "sr": "Питање",
        "sw": "Swali",
        "th": "คำถาม",
        "tl": "Tanong",
        "pt-BR": "Pergunta",
        "es-LATAM": "Pregunta",
        "zh-TW": "問題",
    },
    "answer": {
        "en": "Answer",
        "es": "Respuesta",
        "fr": "Réponse",
        "de": "Antwort",
        "it": "Risposta",
        "pt": "Resposta",
        "ru": "Ответ",
        "zh": "答案",
        "ja": "回答",
        "ko": "답변",
        "nl": "Antwoord",
        "pl": "Odpowiedź",
        "sv": "Svar",
        "tr": "Cevap",
        "uk": "Відповідь",
        "vi": "Câu trả lời",
        "ar": "إجابة",
        "bg": "Отговор",
        "cs": "Odpověď",
        "da": "Svar",
        "el": "Απάντηση",
        "fa": "پاسخ",
        "he": "תשובה",
        "hi": "उत्तर",
        "hr": "Odgovor",
        "hu": "Válasz",
        "id": "Jawaban",
        "lt": "Atsakymas",
        "lv": "Atbilde",
        "ms": "Jawapan",
        "no": "Svar",
        "ro": "Răspuns",
        "sk": "Odpoveď",
        "sl": "Odgovor",
        "sr": "Одговор",
        "sw": "Jibu",
        "th": "คำตอบ",
        "tl": "Sagot",
        "pt-BR": "Resposta",
        "es-LATAM": "Respuesta",
        "zh-TW": "答案",
    },
    "relevantPolicyContext": {
        "en": "Relevant Policy Context",
        "es": "Contexto de Política Relevante",
        "fr": "Contexte de Politique Pertinent",
        "de": "Relevanter Richtlinienkontext",
        "it": "Contesto di Politica Rilevante",
        "pt": "Contexto de Política Relevante",
        "ru": "Соответствующий Контекст Политики",
        "zh": "相关政策背景",
        "ja": "関連するポリシーコンテキスト",
        "ko": "관련 정책 컨텍스트",
        "nl": "Relevante Beleidscontext",
        "pl": "Odpowiedni Kontekst Polityki",
        "sv": "Relevant Policykontext",
        "tr": "İlgili Politika Bağlamı",
        "uk": "Відповідний Контекст Політики",
        "vi": "Bối Cảnh Chính Sách Liên Quan",
        "ar": "سياق السياسة ذات الصلة",
        "bg": "Съответен Контекст на Политиката",
        "cs": "Relevantní Kontext Politiky",
        "da": "Relevant Politikkontekst",
        "el": "Σχετικό Πλαίσιο Πολιτικής",
        "fa": "زمینه سیاست مرتبط",
        "he": "הקשר מדיניות רלוונטי",
        "hi": "प्रासंगिक नीति संदर्भ",
        "hr": "Relevantan Kontekst Politike",
        "hu": "Releváns Szabályzat Kontextus",
        "id": "Konteks Kebijakan yang Relevan",
        "lt": "Aktualus Politikos Kontekstas",
        "lv": "Atbilstošs Politikas Konteksts",
        "ms": "Konteks Dasar yang Berkaitan",
        "no": "Relevant Policykontekst",
        "ro": "Context de Politică Relevant",
        "sk": "Relevantný Kontext Politiky",
        "sl": "Ustrezen Kontekst Politike",
        "sr": "Релевантан Контекст Политике",
        "sw": "Muktadha wa Sera Husika",
        "th": "บริบทนโยบายที่เกี่ยวข้อง",
        "tl": "Kaugnay na Konteksto ng Patakaran",
        "pt-BR": "Contexto de Política Relevante",
        "es-LATAM": "Contexto de Política Relevante",
        "zh-TW": "相關政策背景",
    },
    "topic": {
        "en": "Topic",
        "es": "Tema",
        "fr": "Sujet",
        "de": "Thema",
        "it": "Argomento",
        "pt": "Tópico",
        "ru": "Тема",
        "zh": "主题",
        "ja": "トピック",
        "ko": "주제",
        "nl": "Onderwerp",
        "pl": "Temat",
        "sv": "Ämne",
        "tr": "Konu",
        "uk": "Тема",
        "vi": "Chủ đề",
        "ar": "موضوع",
        "bg": "Тема",
        "cs": "Téma",
        "da": "Emne",
        "el": "Θέμα",
        "fa": "موضوع",
        "he": "נושא",
        "hi": "विषय",
        "hr": "Tema",
        "hu": "Téma",
        "id": "Topik",
        "lt": "Tema",
        "lv": "Tēma",
        "ms": "Topik",
        "no": "Emne",
        "ro": "Subiect",
        "sk": "Téma",
        "sl": "Tema",
        "sr": "Тема",
        "sw": "Mada",
        "th": "หัวข้อ",
        "tl": "Paksa",
        "pt-BR": "Tópico",
        "es-LATAM": "Tema",
        "zh-TW": "主題",
    },
}

# Get the locales directory
locales_dir = Path("frontend/src/locales")

# Process each language directory
for lang_dir in locales_dir.iterdir():
    if not lang_dir.is_dir():
        continue

    lang_code = lang_dir.name
    common_file = lang_dir / "common.json"

    if not common_file.exists():
        print(f"Skipping {lang_code}: common.json not found")
        continue

    # Read the current JSON
    with open(common_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Check if archive.docxHeaders exists
    if "archive" not in data or "docxHeaders" not in data["archive"]:
        print(f"Skipping {lang_code}: archive.docxHeaders not found")
        continue

    # Add the new keys if they don't exist
    docx_headers = data["archive"]["docxHeaders"]
    modified = False

    for key, translations in new_keys.items():
        if key not in docx_headers:
            # Get translation for this language, fallback to English
            translation = translations.get(lang_code, translations["en"])
            docx_headers[key] = translation
            modified = True
            print(f"Added '{key}' to {lang_code}: {translation}")

    # Write back if modified
    if modified:
        with open(common_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✓ Updated {lang_code}")
    else:
        print(f"- {lang_code} already has all keys")

print("\n✓ All translation files updated!")
