"""
Translation service for converting LLM outputs to user's preferred language.
"""

from typing import Optional
from app.services.llms import invoke_llm, get_default_llm
from app.api.deps import SessionDep, CurrentUser


def get_translation_prompt(text: str, target_language: str) -> str:
    """
    Create a translation prompt for the LLM.
    """
    language_map = {
        # Major European Languages
        "en": "English",
        "es": "Spanish (Europe)",
        "fr": "French",
        "de": "German",
        "it": "Italian",
        "pt": "Portuguese",
        "ru": "Russian",
        "uk": "Ukrainian",
        "pl": "Polish",
        "nl": "Dutch",
        "sv": "Swedish",
        "no": "Norwegian",
        "da": "Danish",
        "fi": "Finnish",
        "cs": "Czech",
        "sk": "Slovak",
        "hu": "Hungarian",
        "ro": "Romanian",
        "bg": "Bulgarian",
        "hr": "Croatian",
        "sr": "Serbian",
        "sl": "Slovenian",
        "et": "Estonian",
        "lv": "Latvian",
        "lt": "Lithuanian",
        "el": "Greek",
        # Asian Languages
        "zh": "Chinese (Simplified)",
        "zh-TW": "Chinese (Traditional)",
        "ja": "Japanese",
        "ko": "Korean",
        "hi": "Hindi",
        "th": "Thai",
        "vi": "Vietnamese",
        "id": "Indonesian",
        "ms": "Malay",
        "tl": "Filipino",
        # Middle Eastern & African Languages
        "ar": "Arabic",
        "he": "Hebrew",
        "fa": "Persian (Farsi)",
        "tr": "Turkish",
        "sw": "Swahili",
        # Regional Variants
        "pt-BR": "Portuguese (Brazil)",
        "es-LATAM": "Spanish (Latin America)",
    }

    target_language_name = language_map.get(target_language, target_language)

    return f"""You are a professional translator. Translate the following text to {target_language_name}.

IMPORTANT INSTRUCTIONS:
1. Maintain the exact same formatting (markdown tables, headers, lists, etc.)
2. Preserve all technical terms, field names, and document filenames exactly as they are
3. Only translate descriptive text, analysis, and explanations
4. Keep the structure and layout identical
5. If there are markdown tables, preserve the table structure and translate only the content cells, not headers with filenames
6. Do not add any explanations or additional text

Text to translate:
{text}

Translated text:"""


async def translate_text_if_needed(
    text: str, session: SessionDep, current_user: CurrentUser, llm=None
) -> str:
    """
    Translate text to user's preferred language if it's not English.

    Args:
        text: The text to potentially translate
        session: Database session
        current_user: Current user object
        llm: Optional LLM instance to use for translation

    Returns:
        Original text if language is English, translated text otherwise
    """
    # Check user's preferred language
    user_language = getattr(current_user, "preferred_language", "en")

    # If language is English or not set, return original text
    if not user_language or user_language == "en":
        return text

    try:
        # Get LLM for translation if not provided
        if llm is None:
            llm = get_default_llm(session, current_user)

        # Create translation prompt
        translation_prompt = get_translation_prompt(text, user_language)

        # Invoke LLM for translation
        translated_text = invoke_llm(llm, translation_prompt)

        # Extract content if it's a message object
        if hasattr(translated_text, "content"):
            translated_text = translated_text.content

        return str(translated_text).strip()

    except Exception as e:
        # If translation fails, log the error and return original text
        print(f"Translation failed for language '{user_language}': {str(e)}")
        return text


def get_supported_languages() -> dict:
    """
    Get the list of supported languages for translation.

    Returns:
        Dictionary mapping language codes to language names
    """
    return {
        # Major European Languages
        "en": "English",
        "es": "Spanish (Europe)",
        "fr": "French",
        "de": "German",
        "it": "Italian",
        "pt": "Portuguese",
        "ru": "Russian",
        "uk": "Ukrainian",
        "pl": "Polish",
        "nl": "Dutch",
        "sv": "Swedish",
        "no": "Norwegian",
        "da": "Danish",
        "fi": "Finnish",
        "cs": "Czech",
        "sk": "Slovak",
        "hu": "Hungarian",
        "ro": "Romanian",
        "bg": "Bulgarian",
        "hr": "Croatian",
        "sr": "Serbian",
        "sl": "Slovenian",
        "et": "Estonian",
        "lv": "Latvian",
        "lt": "Lithuanian",
        "el": "Greek",
        # Asian Languages
        "zh": "Chinese (Simplified)",
        "zh-TW": "Chinese (Traditional)",
        "ja": "Japanese",
        "ko": "Korean",
        "hi": "Hindi",
        "th": "Thai",
        "vi": "Vietnamese",
        "id": "Indonesian",
        "ms": "Malay",
        "tl": "Filipino",
        # Middle Eastern & African Languages
        "ar": "Arabic",
        "he": "Hebrew",
        "fa": "Persian (Farsi)",
        "tr": "Turkish",
        "sw": "Swahili",
        # Regional Variants
        "pt-BR": "Portuguese (Brazil)",
        "es-LATAM": "Spanish (Latin America)",
    }


def is_translation_needed(current_user: CurrentUser) -> bool:
    """
    Check if translation is needed for the current user.

    Args:
        current_user: Current user object

    Returns:
        True if translation is needed, False otherwise
    """
    user_language = getattr(current_user, "preferred_language", "en")
    return user_language and user_language != "en"
