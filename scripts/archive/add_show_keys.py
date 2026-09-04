#!/usr/bin/env python3
"""
Add showMore, showLess, and readMore keys to all common.json files.
"""

import json
import os
from pathlib import Path


def add_keys_to_common_json(lang_file_path):
    """Add the new keys to a common.json file."""
    with open(lang_file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "common" not in data:
        data["common"] = {}

    common = data["common"]

    # Add the keys if they don't exist
    if "showMore" not in common:
        common["showMore"] = "[TODO: Show More]"
    if "showLess" not in common:
        common["showLess"] = "[TODO: Show Less]"
    if "readMore" not in common:
        common["readMore"] = "[TODO: Read More]"
    if "questionNumber" not in common:
        common["questionNumber"] = "[TODO: Question {{number}}:]"
    if "viewSourceCitations" not in common:
        common["viewSourceCitations"] = "[TODO: View Source Citations ({{count}})]"
    if "answer" not in common:
        common["answer"] = "[TODO: Answer:]"
    if "relevantPolicyContext" not in common:
        common["relevantPolicyContext"] = "[TODO: Relevant Policy Context:]"
    if "sources" not in common:
        common["sources"] = "[TODO: sources]"
    if "sourceCitations" not in common:
        common["sourceCitations"] = "[TODO: Source Citations ({{count}})]"
    if "citationNumber" not in common:
        common["citationNumber"] = "[TODO: Citation {{number}}]"
    if "noSourceCitations" not in common:
        common["noSourceCitations"] = (
            "[TODO: No source citations available for this section]"
        )
    if "noDetailedSections" not in common:
        common["noDetailedSections"] = (
            "[TODO: No detailed sections available for this report]"
        )
    if "topicLabel" not in common:
        common["topicLabel"] = "[TODO: Topic:]"
    if "knowledgeBaseReference" not in common:
        common["knowledgeBaseReference"] = "[TODO: Knowledge Base Reference]"
    if "knowledgeBaseReferences" not in common:
        common["knowledgeBaseReferences"] = "[TODO: Knowledge Base References]"
    if "hideReferences" not in common:
        common["hideReferences"] = "[TODO: Hide References]"
    if "showReferences" not in common:
        common["showReferences"] = "[TODO: Show References]"
    if "referenceNumber" not in common:
        common["referenceNumber"] = "[TODO: Reference {{number}}]"
    if "processedInChunks" not in common:
        common["processedInChunks"] = "[TODO: Processed in {{count}} chunks]"
    if "synthesisErrorNote" not in common:
        common["synthesisErrorNote"] = (
            "[TODO: Note: Synthesis error occurred - showing combined chunk results]"
        )

    # Ensure proper ordering - put them after 'cut' if it exists
    if "cut" in common:
        # Reorder to put the new keys after 'cut'
        ordered_common = {}
        for key, value in common.items():
            ordered_common[key] = value
            if key == "cut":
                ordered_common["showMore"] = common.get("showMore", "[TODO: Show More]")
                ordered_common["showLess"] = common.get("showLess", "[TODO: Show Less]")
                ordered_common["readMore"] = common.get("readMore", "[TODO: Read More]")
                ordered_common["questionNumber"] = common.get(
                    "questionNumber", "[TODO: Question {{number}}:]]"
                )
                ordered_common["viewSourceCitations"] = common.get(
                    "viewSourceCitations", "[TODO: View Source Citations ({{count}})]"
                )
                ordered_common["answer"] = common.get("answer", "[TODO: Answer:]")
                ordered_common["relevantPolicyContext"] = common.get(
                    "relevantPolicyContext", "[TODO: Relevant Policy Context:]"
                )
                ordered_common["sources"] = common.get("sources", "[TODO: sources]")
                ordered_common["sourceCitations"] = common.get(
                    "sourceCitations", "[TODO: Source Citations ({{count}})]"
                )
                ordered_common["citationNumber"] = common.get(
                    "citationNumber", "[TODO: Citation {{number}}]"
                )
                ordered_common["noSourceCitations"] = common.get(
                    "noSourceCitations",
                    "[TODO: No source citations available for this section]",
                )
                ordered_common["noDetailedSections"] = common.get(
                    "noDetailedSections",
                    "[TODO: No detailed sections available for this report]",
                )
                ordered_common["topicLabel"] = common.get(
                    "topicLabel", "[TODO: Topic:]"
                )
                ordered_common["knowledgeBaseReference"] = common.get(
                    "knowledgeBaseReference", "[TODO: Knowledge Base Reference]"
                )
                ordered_common["knowledgeBaseReferences"] = common.get(
                    "knowledgeBaseReferences", "[TODO: Knowledge Base References]"
                )
                ordered_common["hideReferences"] = common.get(
                    "hideReferences", "[TODO: Hide References]"
                )
                ordered_common["showReferences"] = common.get(
                    "showReferences", "[TODO: Show References]"
                )
                ordered_common["referenceNumber"] = common.get(
                    "referenceNumber", "[TODO: Reference {{number}}]"
                )
                ordered_common["processedInChunks"] = common.get(
                    "processedInChunks", "[TODO: Processed in {{count}} chunks]"
                )
                ordered_common["synthesisErrorNote"] = common.get(
                    "synthesisErrorNote",
                    "[TODO: Note: Synthesis error occurred - showing combined chunk results]",
                )
        data["common"] = ordered_common

    with open(lang_file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Updated {lang_file_path}")


def main():
    locales_dir = Path(__file__).parent / "frontend" / "src" / "locales"

    # Get all language directories
    lang_dirs = [
        d for d in locales_dir.iterdir() if d.is_dir() and (d / "common.json").exists()
    ]

    for lang_dir in sorted(lang_dirs):
        lang_code = lang_dir.name
        common_file = lang_dir / "common.json"
        add_keys_to_common_json(common_file)

    print(
        "All common.json files have been updated with showMore, showLess, and readMore keys."
    )


if __name__ == "__main__":
    main()
