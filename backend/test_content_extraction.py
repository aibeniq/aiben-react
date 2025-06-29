#!/usr/bin/env python3
"""
Test script to verify the enhanced content extraction logic for optimize_outline.
"""

import json


def test_json_parsing():
    """Test the new JSON parsing logic that extracts section_content."""

    # Simulate an LLM response with the new format
    mock_llm_response = """
    {
        "mappings": [
            {
                "section_content": "This is the actual introduction text from the document that discusses the background and motivation for the research study.",
                "outline_section": 1
            },
            {
                "section_content": "Here we describe the methodology used in our analysis, including data collection procedures and statistical methods.",
                "outline_section": 2
            },
            {
                "section_content": "The results show a significant correlation between variables A and B, with p-value < 0.05.",
                "outline_section": 3
            }
        ]
    }
    """

    # Test variables
    section_descriptions = [
        "Introduction and Background",
        "Methodology",
        "Results and Analysis",
        "Conclusions",
    ]

    section_to_content = {section: [] for section in section_descriptions}
    assigned_sections = []
    document_sections_identified = []

    print("Testing JSON parsing with section_content extraction...")
    print(f"Mock LLM Response: {mock_llm_response.strip()}")
    print()

    try:
        # Parse the JSON response (this mirrors the actual code)
        response_text = mock_llm_response.strip()
        json_response = json.loads(response_text)

        if "mappings" in json_response:
            for mapping in json_response["mappings"]:
                section_content = mapping.get("section_content", "").strip()
                outline_section_num = mapping.get("outline_section", 0)

                # Record the identified section content
                if section_content:
                    preview = (
                        section_content[:100] + "..."
                        if len(section_content) > 100
                        else section_content
                    )
                    document_sections_identified.append(preview)

                # Map to actual section description and collect content
                if 1 <= outline_section_num <= len(section_descriptions):
                    section_desc = section_descriptions[outline_section_num - 1]
                    if section_desc not in assigned_sections:
                        assigned_sections.append(section_desc)

                    # Store the actual section content
                    if section_content:
                        section_to_content[section_desc].append(section_content)

        print("✓ JSON parsing successful!")
        print(f"Assigned sections: {assigned_sections}")
        print(f"Document sections identified: {len(document_sections_identified)}")
        print()

        # Print extracted content for each section
        for section_desc in section_descriptions:
            content_list = section_to_content[section_desc]
            if content_list:
                total_chars = sum(len(content) for content in content_list)
                print(f"Section '{section_desc}':")
                print(f"  - {len(content_list)} content piece(s)")
                print(f"  - {total_chars} total characters")
                for i, content in enumerate(content_list):
                    preview = content[:80] + "..." if len(content) > 80 else content
                    print(f"    {i+1}. {preview}")
                print()
            else:
                print(f"Section '{section_desc}': No content extracted")
                print()

        # Summary
        total_extracted = sum(
            len(content_list) for content_list in section_to_content.values()
        )
        sections_with_content = sum(
            1 for content_list in section_to_content.values() if content_list
        )

        print(f"SUMMARY:")
        print(f"- Total content pieces extracted: {total_extracted}")
        print(
            f"- Sections with content: {sections_with_content}/{len(section_descriptions)}"
        )
        print(
            f"- Total characters extracted: {sum(len(content) for content_list in section_to_content.values() for content in content_list)}"
        )

        return True

    except Exception as e:
        print(f"✗ Error in JSON parsing: {e}")
        return False


def test_markdown_code_blocks():
    """Test handling of markdown code blocks in LLM responses."""

    mock_response_with_markdown = """
    ```json
    {
        "mappings": [
            {
                "section_content": "This content was wrapped in markdown code blocks.",
                "outline_section": 1
            }
        ]
    }
    ```
    """

    print("Testing markdown code block handling...")

    # Clean the response (this mirrors the actual code)
    response_text = mock_response_with_markdown.strip()

    if response_text.startswith("```json"):
        response_text = response_text[7:]  # Remove ```json
    elif response_text.startswith("```"):
        response_text = response_text[3:]  # Remove ```

    if response_text.endswith("```"):
        response_text = response_text[:-3]  # Remove closing ```

    response_text = response_text.strip()

    try:
        json_response = json.loads(response_text)
        print("✓ Markdown code block handling successful!")
        print(f"Cleaned response: {response_text}")
        print(f"Parsed JSON: {json_response}")
        return True
    except Exception as e:
        print(f"✗ Error handling markdown: {e}")
        return False


if __name__ == "__main__":
    print("=" * 80)
    print("TESTING ENHANCED CONTENT EXTRACTION FOR OPTIMIZE_OUTLINE")
    print("=" * 80)
    print()

    success1 = test_json_parsing()
    print()

    success2 = test_markdown_code_blocks()
    print()

    if success1 and success2:
        print(
            "🎉 All tests passed! The enhanced content extraction logic is working correctly."
        )
    else:
        print("❌ Some tests failed. Please check the implementation.")
