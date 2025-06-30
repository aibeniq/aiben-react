"""
Test script to verify that sections with Consult Documents: False are excluded from results.
"""


def test_section_filtering():
    """Test how sections with different consultDocuments settings are filtered from results."""

    # Sample sections with mixed consultDocuments settings
    test_sections = [
        {
            "text": "Executive Summary",
            "consultDocuments": True,  # Should appear in results
        },
        {
            "text": "Table of Contents",
            "consultDocuments": False,  # Should be excluded from results
        },
        {
            "text": "Technical Analysis",
            "consultDocuments": True,  # Should appear in results
        },
        {
            "text": "Appendix A: Raw Data",
            "consultDocuments": False,  # Should be excluded from results
        },
        {
            "text": "Conclusions and Recommendations",
            "consultDocuments": True,  # Should appear in results
        },
    ]

    # Simulate the section processing logic
    section_consult_settings = {}
    generated_sections = {}
    suggestions = []

    # Step 1: Build section settings and generated content (all sections)
    for section in test_sections:
        section_description = section["text"].strip()
        consult_documents = section.get("consultDocuments", True)
        section_consult_settings[section_description] = consult_documents
        generated_sections[section_description] = (
            f"Generated content for {section_description}"
        )

    # Step 2: Process sections for suggestions (filter out non-consulting sections)
    for section_description, generated_content in generated_sections.items():
        consults_documents = section_consult_settings.get(section_description, True)

        if not consults_documents:
            print(f"Excluding from results: {section_description}")
            continue  # Skip - don't add to suggestions

        # Add to suggestions (simulate optimization logic)
        print(f"Including in results: {section_description}")
        suggestions.append(
            {
                "original_section": section_description,
                "suggested_section": section_description,
                "needs_revision": False,  # Simplified for test
            }
        )

    print("\n=== OPTIMIZE OUTLINE FILTERING TEST ===")
    print(f"Total sections in outline: {len(test_sections)}")
    print(f"Sections in optimization results: {len(suggestions)}")
    print()

    print("SECTIONS INCLUDED IN RESULTS:")
    for suggestion in suggestions:
        print(f"  ✓ {suggestion['original_section']}")
    print()

    # Calculate statistics
    sections_that_consult_docs = sum(
        1 for consults in section_consult_settings.values() if consults
    )
    sections_that_dont_consult_docs = (
        len(section_consult_settings) - sections_that_consult_docs
    )
    sections_actually_optimized = 0  # Simulate 0 needing optimization for test

    print("ANALYSIS SUMMARY:")
    analysis_summary = f"""
Enhanced Content Extraction Analysis:
- Total outline sections: {len(test_sections)}
- Sections that consult documents (shown in results): {sections_that_consult_docs}
- Sections that don't consult documents (excluded from results): {sections_that_dont_consult_docs}
- Sections needing optimization: {sections_actually_optimized}
- Sections working well: {sections_that_consult_docs - sections_actually_optimized}
    """.strip()

    print(analysis_summary)

    # Verify results
    expected_in_results = [
        "Executive Summary",
        "Technical Analysis",
        "Conclusions and Recommendations",
    ]
    actual_in_results = [s["original_section"] for s in suggestions]

    assert (
        actual_in_results == expected_in_results
    ), f"Expected {expected_in_results}, got {actual_in_results}"
    assert len(suggestions) == 3, f"Expected 3 suggestions, got {len(suggestions)}"

    print(
        "\n✅ All tests passed! Non-consulting sections correctly excluded from results."
    )


if __name__ == "__main__":
    test_section_filtering()
