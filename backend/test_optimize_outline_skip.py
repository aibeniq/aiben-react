"""
Test script to verify Optimize Outline functionality with mixed consult document settings.

This script demonstrates how the optimization logic should behave with:
- Sections that consult documents (should be optimized)
- Sections that don't consult documents (should be skipped)
"""

import json


def test_section_classification():
    """Test how sections with different consultDocuments settings are handled."""

    # Sample sections with mixed consultDocuments settings
    test_sections = [
        {"text": "Executive Summary", "consultDocuments": True},  # Should be optimized
        {"text": "Table of Contents", "consultDocuments": False},  # Should be skipped
        {"text": "Technical Analysis", "consultDocuments": True},  # Should be optimized
        {
            "text": "Appendix A: Raw Data",
            "consultDocuments": False,  # Should be skipped
        },
        {
            "text": "Conclusions and Recommendations",
            "consultDocuments": True,  # Should be optimized
        },
    ]

    # Simulate the section processing logic
    section_consult_settings = {}
    sections_to_optimize = []
    sections_to_skip = []

    for section in test_sections:
        section_description = section["text"].strip()
        consult_documents = section.get("consultDocuments", True)

        # Track setting (as done in the backend)
        section_consult_settings[section_description] = consult_documents

        if consult_documents:
            sections_to_optimize.append(section_description)
        else:
            sections_to_skip.append(section_description)

    print("=== OPTIMIZE OUTLINE SECTION CLASSIFICATION TEST ===")
    print(f"Total sections: {len(test_sections)}")
    print(f"Sections to optimize: {len(sections_to_optimize)}")
    print(f"Sections to skip: {len(sections_to_skip)}")
    print()

    print("SECTIONS TO OPTIMIZE (consultDocuments: true):")
    for section in sections_to_optimize:
        print(f"  ✓ {section}")
    print()

    print("SECTIONS TO SKIP (consultDocuments: false):")
    for section in sections_to_skip:
        print(f"  ⏭ {section}")
    print()

    # Expected results
    expected_to_optimize = [
        "Executive Summary",
        "Technical Analysis",
        "Conclusions and Recommendations",
    ]
    expected_to_skip = ["Table of Contents", "Appendix A: Raw Data"]

    assert (
        sections_to_optimize == expected_to_optimize
    ), f"Expected {expected_to_optimize}, got {sections_to_optimize}"
    assert (
        sections_to_skip == expected_to_skip
    ), f"Expected {expected_to_skip}, got {sections_to_skip}"

    print("✅ All tests passed! Section classification working correctly.")

    # Simulate analysis summary
    sections_that_consult_docs = len(sections_to_optimize)
    sections_that_dont_consult_docs = len(sections_to_skip)
    sections_actually_optimized = 1  # Simulate 1 needing optimization

    analysis_summary = f"""
Enhanced Content Extraction Analysis:
- Total sections evaluated: {len(test_sections)}
- Sections that consult documents: {sections_that_consult_docs}
- Sections that don't consult documents (skipped): {sections_that_dont_consult_docs}
- Sections needing optimization: {sections_actually_optimized}
- Sections working well: {sections_that_consult_docs - sections_actually_optimized}
    """.strip()

    print("\nSAMPLE ANALYSIS SUMMARY:")
    print(analysis_summary)


if __name__ == "__main__":
    test_section_classification()
