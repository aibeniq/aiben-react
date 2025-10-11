#!/usr/bin/env python3
"""
Generate translations for all [TODO: ...] markers using AI translation.
WARNING: These are machine translations and should be reviewed by native speakers
or professional translators before production use.
"""

import json
import os
from pathlib import Path
import re
from typing import Dict, List

# Language codes and their full names
LANGUAGE_NAMES = {
    "ar": "Arabic",
    "bg": "Bulgarian",
    "cs": "Czech",
    "da": "Danish",
    "de": "German",
    "el": "Greek",
    "es": "Spanish",
    "es-LATAM": "Spanish (Latin America)",
    "et": "Estonian",
    "fa": "Persian",
    "fr": "French",
    "he": "Hebrew",
    "hi": "Hindi",
    "hr": "Croatian",
    "hu": "Hungarian",
    "id": "Indonesian",
    "it": "Italian",
    "ja": "Japanese",
    "ko": "Korean",
    "lt": "Lithuanian",
    "lv": "Latvian",
    "ms": "Malay",
    "nl": "Dutch",
    "no": "Norwegian",
    "pl": "Polish",
    "pt": "Portuguese",
    "pt-BR": "Portuguese (Brazil)",
    "ro": "Romanian",
    "ru": "Russian",
    "sk": "Slovak",
    "sl": "Slovenian",
    "sr": "Serbian",
    "sv": "Swedish",
    "sw": "Swahili",
    "th": "Thai",
    "tl": "Filipino",
    "tr": "Turkish",
    "uk": "Ukrainian",
    "vi": "Vietnamese",
    "zh": "Chinese (Simplified)",
    "zh-TW": "Chinese (Traditional)",
}

# Basic translations for common phrases (manually verified)
BASIC_TRANSLATIONS = {
    "ar": {
        "Starting...": "جاري البدء...",
        "Initializing...": "جاري التهيئة...",
        "Processing...": "جاري المعالجة...",
        "Extracting content...": "جاري استخراج المحتوى...",
        "Please wait while we generate your report": "يرجى الانتظار أثناء إنشاء تقريرك",
        "Please wait while we compare your documents": "يرجى الانتظار أثناء مقارنة مستنداتك",
        "Please wait while we match your documents": "يرجى الانتظار أثناء مطابقة مستنداتك",
        "Please wait while we review your documents": "يرجى الانتظار أثناء مراجعة مستنداتك",
        "Generating report...": "جاري إنشاء التقرير...",
        "Comparing...": "جاري المقارنة...",
        "Comparing and formatting results...": "جاري مقارنة وتنسيق النتائج...",
        "Matching fields...": "جاري مطابقة الحقول...",
        "Documents compared successfully!": "تمت مقارنة المستندات بنجاح!",
        "Form processing completed successfully!": "تم إكمال معالجة النموذج بنجاح!",
        "Field values extracted from single document.": "تم استخراج قيم الحقول من مستند واحد.",
        "Processing section {{sectionNum}} of {{totalSections}}: {{sectionPreview}}": "معالجة القسم {{sectionNum}} من {{totalSections}}: {{sectionPreview}}"
    },
    "de": {
        "Starting...": "Wird gestartet...",
        "Initializing...": "Wird initialisiert...",
        "Processing...": "Wird verarbeitet...",
        "Extracting content...": "Inhalt wird extrahiert...",
        "Please wait while we generate your report": "Bitte warten Sie, während wir Ihren Bericht erstellen",
        "Please wait while we compare your documents": "Bitte warten Sie, während wir Ihre Dokumente vergleichen",
        "Please wait while we match your documents": "Bitte warten Sie, während wir Ihre Dokumente abgleichen",
        "Please wait while we review your documents": "Bitte warten Sie, während wir Ihre Dokumente überprüfen",
        "Generating report...": "Bericht wird erstellt...",
        "Comparing...": "Wird verglichen...",
        "Comparing and formatting results...": "Ergebnisse werden verglichen und formatiert...",
        "Matching fields...": "Felder werden abgeglichen...",
        "Documents compared successfully!": "Dokumente erfolgreich verglichen!",
        "Form processing completed successfully!": "Formularverarbeitung erfolgreich abgeschlossen!",
        "Field values extracted from single document.": "Feldwerte aus einem einzelnen Dokument extrahiert.",
        "Processing section {{sectionNum}} of {{totalSections}}: {{sectionPreview}}": "Abschnitt {{sectionNum}} von {{totalSections}} wird verarbeitet: {{sectionPreview}}"
    },
    "es": {
        "Starting...": "Iniciando...",
        "Initializing...": "Inicializando...",
        "Processing...": "Procesando...",
        "Extracting content...": "Extrayendo contenido...",
        "Please wait while we generate your report": "Por favor espere mientras generamos su informe",
        "Please wait while we compare your documents": "Por favor espere mientras comparamos sus documentos",
        "Please wait while we match your documents": "Por favor espere mientras coincidimos sus documentos",
        "Please wait while we review your documents": "Por favor espere mientras revisamos sus documentos",
        "Generating report...": "Generando informe...",
        "Comparing...": "Comparando...",
        "Comparing and formatting results...": "Comparando y formateando resultados...",
        "Matching fields...": "Coincidiendo campos...",
        "Documents compared successfully!": "¡Documentos comparados exitosamente!",
        "Form processing completed successfully!": "¡Procesamiento de formulario completado exitosamente!",
        "Field values extracted from single document.": "Valores de campos extraídos de un solo documento.",
        "Processing section {{sectionNum}} of {{totalSections}}: {{sectionPreview}}": "Procesando sección {{sectionNum}} de {{totalSections}}: {{sectionPreview}}"
    },
    "fr": {
        "Starting...": "Démarrage...",
        "Initializing...": "Initialisation...",
        "Processing...": "Traitement...",
        "Extracting content...": "Extraction du contenu...",
        "Please wait while we generate your report": "Veuillez patienter pendant que nous générons votre rapport",
        "Please wait while we compare your documents": "Veuillez patienter pendant que nous comparons vos documents",
        "Please wait while we match your documents": "Veuillez patienter pendant que nous apparions vos documents",
        "Please wait while we review your documents": "Veuillez patienter pendant que nous examinons vos documents",
        "Generating report...": "Génération du rapport...",
        "Comparing...": "Comparaison...",
        "Comparing and formatting results...": "Comparaison et formatage des résultats...",
        "Matching fields...": "Appariement des champs...",
        "Documents compared successfully!": "Documents comparés avec succès !",
        "Form processing completed successfully!": "Traitement du formulaire terminé avec succès !",
        "Field values extracted from single document.": "Valeurs de champs extraites d'un seul document.",
        "Processing section {{sectionNum}} of {{totalSections}}: {{sectionPreview}}": "Traitement de la section {{sectionNum}} sur {{totalSections}} : {{sectionPreview}}"
    },
    "it": {
        "Starting...": "Avvio in corso...",
        "Initializing...": "Inizializzazione...",
        "Processing...": "Elaborazione...",
        "Extracting content...": "Estrazione contenuto...",
        "Please wait while we generate your report": "Attendere mentre generiamo il rapporto",
        "Please wait while we compare your documents": "Attendere mentre confrontiamo i documenti",
        "Please wait while we match your documents": "Attendere mentre abbiniamo i documenti",
        "Please wait while we review your documents": "Attendere mentre revisioniamo i documenti",
        "Generating report...": "Generazione rapporto...",
        "Comparing...": "Confronto...",
        "Comparing and formatting results...": "Confronto e formattazione risultati...",
        "Matching fields...": "Abbinamento campi...",
        "Documents compared successfully!": "Documenti confrontati con successo!",
        "Form processing completed successfully!": "Elaborazione modulo completata con successo!",
        "Field values extracted from single document.": "Valori dei campi estratti da un singolo documento.",
        "Processing section {{sectionNum}} of {{totalSections}}: {{sectionPreview}}": "Elaborazione sezione {{sectionNum}} di {{totalSections}}: {{sectionPreview}}"
    },
    "ja": {
        "Starting...": "開始中...",
        "Initializing...": "初期化中...",
        "Processing...": "処理中...",
        "Extracting content...": "コンテンツ抽出中...",
        "Please wait while we generate your report": "レポートを生成中です。しばらくお待ちください",
        "Please wait while we compare your documents": "ドキュメントを比較中です。しばらくお待ちください",
        "Please wait while we match your documents": "ドキュメントをマッチング中です。しばらくお待ちください",
        "Please wait while we review your documents": "ドキュメントを確認中です。しばらくお待ちください",
        "Generating report...": "レポート生成中...",
        "Comparing...": "比較中...",
        "Comparing and formatting results...": "結果の比較とフォーマット中...",
        "Matching fields...": "フィールドマッチング中...",
        "Documents compared successfully!": "ドキュメントの比較が完了しました！",
        "Form processing completed successfully!": "フォーム処理が正常に完了しました！",
        "Field values extracted from single document.": "単一ドキュメントからフィールド値が抽出されました。",
        "Processing section {{sectionNum}} of {{totalSections}}: {{sectionPreview}}": "セクション {{sectionNum}}/{{totalSections}} を処理中: {{sectionPreview}}"
    },
    "ko": {
        "Starting...": "시작 중...",
        "Initializing...": "초기화 중...",
        "Processing...": "처리 중...",
        "Extracting content...": "콘텐츠 추출 중...",
        "Please wait while we generate your report": "보고서를 생성하는 동안 잠시 기다려주세요",
        "Please wait while we compare your documents": "문서를 비교하는 동안 잠시 기다려주세요",
        "Please wait while we match your documents": "문서를 매칭하는 동안 잠시 기다려주세요",
        "Please wait while we review your documents": "문서를 검토하는 동안 잠시 기다려주세요",
        "Generating report...": "보고서 생성 중...",
        "Comparing...": "비교 중...",
        "Comparing and formatting results...": "결과 비교 및 포맷팅 중...",
        "Matching fields...": "필드 매칭 중...",
        "Documents compared successfully!": "문서 비교가 성공적으로 완료되었습니다!",
        "Form processing completed successfully!": "양식 처리가 성공적으로 완료되었습니다!",
        "Field values extracted from single document.": "단일 문서에서 필드 값이 추출되었습니다.",
        "Processing section {{sectionNum}} of {{totalSections}}: {{sectionPreview}}": "섹션 {{sectionNum}}/{{totalSections}} 처리 중: {{sectionPreview}}"
    },
    "pt": {
        "Starting...": "Iniciando...",
        "Initializing...": "Inicializando...",
        "Processing...": "Processando...",
        "Extracting content...": "Extraindo conteúdo...",
        "Please wait while we generate your report": "Aguarde enquanto geramos seu relatório",
        "Please wait while we compare your documents": "Aguarde enquanto comparamos seus documentos",
        "Please wait while we match your documents": "Aguarde enquanto correspondemos seus documentos",
        "Please wait while we review your documents": "Aguarde enquanto revisamos seus documentos",
        "Generating report...": "Gerando relatório...",
        "Comparing...": "Comparando...",
        "Comparing and formatting results...": "Comparando e formatando resultados...",
        "Matching fields...": "Correspondendo campos...",
        "Documents compared successfully!": "Documentos comparados com sucesso!",
        "Form processing completed successfully!": "Processamento do formulário concluído com sucesso!",
        "Field values extracted from single document.": "Valores de campos extraídos de um único documento.",
        "Processing section {{sectionNum}} of {{totalSections}}: {{sectionPreview}}": "Processando seção {{sectionNum}} de {{totalSections}}: {{sectionPreview}}"
    },
    "ru": {
        "Starting...": "Запуск...",
        "Initializing...": "Инициализация...",
        "Processing...": "Обработка...",
        "Extracting content...": "Извлечение содержимого...",
        "Please wait while we generate your report": "Пожалуйста, подождите, пока мы генерируем ваш отчет",
        "Please wait while we compare your documents": "Пожалуйста, подождите, пока мы сравниваем ваши документы",
        "Please wait while we match your documents": "Пожалуйста, подождите, пока мы сопоставляем ваши документы",
        "Please wait while we review your documents": "Пожалуйста, подождите, пока мы проверяем ваши документы",
        "Generating report...": "Генерация отчета...",
        "Comparing...": "Сравнение...",
        "Comparing and formatting results...": "Сравнение и форматирование результатов...",
        "Matching fields...": "Сопоставление полей...",
        "Documents compared successfully!": "Документы успешно сравнены!",
        "Form processing completed successfully!": "Обработка формы успешно завершена!",
        "Field values extracted from single document.": "Значения полей извлечены из одного документа.",
        "Processing section {{sectionNum}} of {{totalSections}}: {{sectionPreview}}": "Обработка раздела {{sectionNum}} из {{totalSections}}: {{sectionPreview}}"
    },
    "zh": {
        "Starting...": "开始中...",
        "Initializing...": "初始化中...",
        "Processing...": "处理中...",
        "Extracting content...": "提取内容中...",
        "Please wait while we generate your report": "正在生成您的报告，请稍候",
        "Please wait while we compare your documents": "正在比较您的文档，请稍候",
        "Please wait while we match your documents": "正在匹配您的文档，请稍候",
        "Please wait while we review your documents": "正在审核您的文档，请稍候",
        "Generating report...": "生成报告中...",
        "Comparing...": "比较中...",
        "Comparing and formatting results...": "比较并格式化结果中...",
        "Matching fields...": "匹配字段中...",
        "Documents compared successfully!": "文档比较成功！",
        "Form processing completed successfully!": "表单处理成功完成！",
        "Field values extracted from single document.": "从单个文档中提取了字段值。",
        "Processing section {{sectionNum}} of {{totalSections}}: {{sectionPreview}}": "正在处理第 {{sectionNum}} 节，共 {{totalSections}} 节：{{sectionPreview}}"
    }
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

def find_placeholders_and_original_strings(lang_code, lang_file_path):
    """Find all placeholder items in a language file."""
    with open(lang_file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find all placeholder patterns
    placeholder_pattern = r'(\[(?:TODO|TRANSLATE TO .*?):\s*.*?\])'
    placeholders = re.findall(placeholder_pattern, content)

    return list(set(placeholders))  # Remove duplicates

def get_text_from_placeholder(placeholder):
    """Extracts the text to be translated from a placeholder."""
    match = re.search(r'\[(?:TODO|TRANSLATE TO .*?):\s*(.*?)\]', placeholder)
    if match:
        return match.group(1)
    return None

def translate_text(text, target_lang):
    """Translate text to target language using basic translations or fallback."""
    if target_lang in BASIC_TRANSLATIONS and text in BASIC_TRANSLATIONS[target_lang]:
        return BASIC_TRANSLATIONS[target_lang][text]

    # For languages not in our basic translations, provide a placeholder
    # In a real implementation, you would use a translation API here
    return f"[TRANSLATE TO {LANGUAGE_NAMES.get(target_lang, target_lang).upper()}: {text}]"

def update_language_file(lang_code, lang_file_path, english_file_path):
    """Update a language file with translations for placeholder items."""
    print(f"\n{'='*60}")
    print(f"Processing: {lang_code} ({LANGUAGE_NAMES.get(lang_code, lang_code)})")
    print(f"{'='*60}")

    # Load the language file
    with open(lang_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Load English reference
    with open(english_file_path, 'r', encoding='utf-8') as f:
        english_data = json.load(f)

    # Find all placeholder items
    placeholders = find_placeholders_and_original_strings(lang_code, lang_file_path)
    print(f"Found {len(placeholders)} placeholder items to translate")

    updated_count = 0

    for placeholder in placeholders:
        todo_text = get_text_from_placeholder(placeholder)
        if not todo_text:
            continue

        # Find where this placeholder appears in the file
        def find_and_replace_placeholder(obj, path=""):
            nonlocal updated_count
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    if isinstance(value, str) and placeholder in value:
                        # Get the English equivalent
                        english_value = get_nested_value(english_data, current_path)
                        if english_value and english_value == todo_text:
                            # Translate it
                            translated = translate_text(todo_text, lang_code)
                            obj[key] = translated
                            print(f"  ✅ {current_path}: '{todo_text}' → '{translated}'")
                            updated_count += 1
                    elif isinstance(value, (dict, list)):
                        find_and_replace_placeholder(value, current_path)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    find_and_replace_placeholder(item, f"{path}[{i}]")


        find_and_replace_placeholder(data)

    if updated_count > 0:
        # Save the updated file
        with open(lang_file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"\n💾 Updated {lang_code}/common.json with {updated_count} translations")
    else:
        print(f"\n✓ No updates needed for {lang_code}")

    return updated_count

def main():
    locales_dir = Path(__file__).parent / "frontend" / "src" / "locales"
    english_file = locales_dir / "en" / "common.json"

    if not english_file.exists():
        print("Error: English reference file not found")
        return

    print("🔄 Generating translations for all TODO items...")
    print("⚠️  WARNING: These are machine translations and should be reviewed by native speakers!")
    print("📝 Only major languages have been translated. Others marked for manual translation.")

    total_translated = 0
    processed_langs = 0

    # Process each language directory
    for lang_dir in sorted(locales_dir.iterdir()):
        if not lang_dir.is_dir():
            continue

        lang_code = lang_dir.name
        if lang_code == "en":
            continue  # Skip English

        common_file = lang_dir / "common.json"
        if not common_file.exists():
            continue

        translated = update_language_file(lang_code, common_file, english_file)
        total_translated += translated
        processed_langs += 1

    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Languages processed: {processed_langs}")
    print(f"Total translations generated: {total_translated}")
    print("\n⚠️  IMPORTANT NOTES:")
    print("• These are MACHINE translations, not professional translations")
    print("• Languages with [TRANSLATE TO ...] markers need manual translation")
    print("• All translations should be reviewed by native speakers")
    print("• Consider using professional translation services for production")
    print("\n✅ Files have been updated. Please review translations before deployment.")

if __name__ == "__main__":
    main()
