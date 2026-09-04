#!/usr/bin/env python3
"""
Add visionAnalysis and pdfParsing translation sections with [TODO] markers to all remaining languages.
"""

import json
import os
from pathlib import Path

# The visionAnalysis and pdfParsing sections to add with TODO markers
VISION_ANALYSIS_SECTION = {
    "visionAnalysis": {
        "tab": "[TODO: Vision Analysis]",
        "title": "[TODO: Vision Analysis Settings]",
        "description": "[TODO: Control whether the AI analyzes images embedded in your documents. Disabling this can significantly reduce API costs for documents with many images.]",
        "enableLabel": "[TODO: Enable Vision Analysis]",
        "costWarning": "[TODO: Warning: Vision analysis can be expensive for documents with many images. Each image analyzed incurs additional API costs. Consider disabling if you primarily work with text-only documents.]",
        "whenEnabled": "[TODO: When enabled:]",
        "feature1": "[TODO: Images in PDFs and DOCX files will be analyzed]",
        "feature2": "[TODO: Charts, diagrams, and visual content will be extracted]",
        "feature3": "[TODO: Form fields in images can be detected (FormConnect)]",
        "feature4": "[TODO: More comprehensive document understanding]",
        "whenDisabled": "[TODO: When disabled:]",
        "disabled1": "[TODO: Only text content will be analyzed (lower cost)]",
        "disabled2": "[TODO: Visual elements in documents will be ignored]",
    }
}

PDF_PARSING_SECTION = {
    "pdfParsing": {
        "tab": "[TODO: PDF Parsing]",
        "title": "[TODO: PDF Parsing Preferences]",
        "description": "[TODO: Control how the system processes PDF documents. Choose the mode that best fits your workflow and document types.]",
        "explanation": "[TODO: Tip: Different parsing modes offer different trade-offs between speed and accuracy. Choose based on your typical document types.]",
        "modeLabel": "[TODO: PDF Parsing Mode]",
        "enhancedMode": "[TODO: Enhanced (Best Quality)]",
        "enhancedDescription": "[TODO: Always uses PyMuPDF4LLM for superior table extraction. Best for documents with complex tables, but slower.]",
        "basicMode": "[TODO: Basic (Fastest)]",
        "basicDescription": "[TODO: Uses fast pypdf extraction only. Best for text-only documents without tables.]",
        "comparison": {
            "title": "[TODO: Mode Comparison:]",
            "enhancedTitle": "[TODO: Enhanced Mode]",
            "enhancedFeature1": "[TODO: Always uses PyMuPDF4LLM]",
            "enhancedFeature2": "[TODO: Best table structure preservation]",
            "enhancedWarning": "[TODO: Slower processing time]",
            "basicTitle": "[TODO: Basic Mode]",
            "basicFeature1": "[TODO: Fastest processing speed]",
            "basicFeature2": "[TODO: Lower resource usage]",
            "basicWarning": "[TODO: May miss table formatting]",
        },
    }
}


def update_language_file(file_path):
    """Update a language file with the new sections."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Ensure settings section exists
        if "settings" not in data:
            data["settings"] = {}

        settings = data["settings"]

        # Add visionAnalysis if it doesn't exist
        if "visionAnalysis" not in settings:
            settings["visionAnalysis"] = VISION_ANALYSIS_SECTION["visionAnalysis"]
            print(f"  Added visionAnalysis section to {file_path}")

        # Add pdfParsing if it doesn't exist
        if "pdfParsing" not in settings:
            settings["pdfParsing"] = PDF_PARSING_SECTION["pdfParsing"]
            print(f"  Added pdfParsing section to {file_path}")

        # Write back the updated file
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return True

    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False


def main():
    locales_dir = Path("frontend/src/locales")

    if not locales_dir.exists():
        print(f"Locales directory not found: {locales_dir}")
        return

    print(
        "Adding visionAnalysis and pdfParsing translation sections with [TODO] markers to all languages..."
    )

    # Languages that already have translations (skip these)
    skip_languages = {"en", "es", "fr", "de", "it"}

    # Get all language directories
    lang_dirs = [
        d
        for d in locales_dir.iterdir()
        if d.is_dir() and (d / "common.json").exists() and d.name not in skip_languages
    ]

    updated_count = 0

    for lang_dir in sorted(lang_dirs):
        lang_code = lang_dir.name
        common_file = lang_dir / "common.json"

        print(f"\nProcessing {lang_code}...")
        if update_language_file(common_file):
            updated_count += 1

    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"Total languages processed: {len(lang_dirs)}")
    print(f"Languages updated: {updated_count}")
    print(f"\nAll files have been updated with [TODO: ...] markers for translation.")
    print(f"Run generate_translations.py to auto-translate these sections.")


if __name__ == "__main__":
    main()
