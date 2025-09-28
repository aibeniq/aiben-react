#!/usr/bin/env python3
"""
Test script to verify JSON table embedding in document content.
This tests the new table processing that embeds JSON metadata in citations.
"""

import json
import sys
import os


def test_json_table_embedding():
    """Test that table data gets properly embedded as JSON in document content."""

    print("🧪 TESTING JSON TABLE EMBEDDING")
    print("=" * 60)

    # Simulate the table data that would come from vision processing
    sample_table_data = {
        "tables": [
            {
                "table_id": "table_1",
                "page": 1,
                "title": "Fee Schedule - Professional Services",
                "headers": ["Service Type", "Base Fee", "Additional Fee", "Notes"],
                "rows": [
                    ["Consultation", "$150", "$50/hour", "Initial consultation"],
                    ["Analysis", "$300", "$100/hour", "Detailed analysis"],
                    ["Report", "$500", "N/A", "Comprehensive report"],
                ],
                "summary": "Professional service fees and rates",
                "context": "This table shows standard fees for various professional services",
                "metadata": {
                    "row_count": 3,
                    "column_count": 4,
                    "table_type": "fee_schedule",
                },
            }
        ]
    }

    # Simulate the document processing
    filename = "Appendix 6 Fee Schedule.pdf"
    page_num = 1
    original_content = (
        "This document contains fee information for professional services."
    )

    # Simulate the new JSON embedding logic
    enhanced_content = original_content

    for table in sample_table_data["tables"]:
        # Create structured JSON representation for table data
        table_json = {
            "table_id": table.get(
                "table_id",
                f"table_{page_num}_{sample_table_data['tables'].index(table)}",
            ),
            "page": page_num,
            "title": table.get("title", table.get("summary", "Data Table")),
            "headers": table.get("headers", []),
            "rows": table.get("rows", []),
            "summary": table.get("summary", ""),
            "context": table.get("context", ""),
            "metadata": {
                "row_count": table.get("metadata", {}).get(
                    "row_count", len(table.get("rows", []))
                ),
                "column_count": table.get("metadata", {}).get(
                    "column_count", len(table.get("headers", []))
                ),
                "table_type": table.get("metadata", {}).get("table_type", "data"),
                "processing_method": "vision_enhanced",
                "source_filename": filename,
                "extraction_timestamp": table.get("metadata", {}).get(
                    "extraction_timestamp", ""
                ),
            },
        }

        # Format as readable JSON for citations
        table_text = f"\n\n=== STRUCTURED TABLE DATA ===\n"
        table_text += json.dumps(table_json, indent=2, ensure_ascii=False)
        table_text += "\n=== END STRUCTURED TABLE DATA ===\n"

        # Also add a human-readable summary for better search capabilities
        table_text += f"\n=== SEARCHABLE SUMMARY ===\n"
        table_text += f"Table: {table_json['title']}\n"

        if table_json["context"]:
            table_text += f"Context: {table_json['context']}\n"

        if table_json["headers"]:
            table_text += f"Columns: {', '.join(table_json['headers'])}\n"

            # Add searchable content for each column
            for header in table_json["headers"]:
                column_index = table_json["headers"].index(header)
                column_values = []

                for row in table_json.get("rows", []):
                    if isinstance(row, list) and column_index < len(row):
                        value = str(row[column_index]).strip()
                        if value and value.lower() not in ["", "null", "none", "n/a"]:
                            column_values.append(value)

                if column_values:
                    sample_values = column_values[:3]  # Reduced for conciseness
                    table_text += f"{header}: {', '.join(sample_values)}"
                    if len(column_values) > 3:
                        table_text += f" (and {len(column_values) - 3} more)"
                    table_text += "\n"

        if table_json["summary"]:
            table_text += f"Summary: {table_json['summary']}\n"

        table_text += f"Dimensions: {table_json['metadata']['row_count']} rows × {table_json['metadata']['column_count']} columns\n"
        table_text += "=== END SEARCHABLE SUMMARY ===\n"

        enhanced_content += table_text

    # Display results
    print("📄 ORIGINAL DOCUMENT CONTENT:")
    print(original_content)
    print("\n" + "=" * 60)

    print("📊 ENHANCED DOCUMENT CONTENT (what users will see in citations):")
    print(enhanced_content)
    print("\n" + "=" * 60)

    # Verify JSON can be parsed
    print("🔍 VERIFICATION:")
    if "=== STRUCTURED TABLE DATA ===" in enhanced_content:
        print("✅ JSON structure markers found")

        # Extract JSON portion
        start_marker = "=== STRUCTURED TABLE DATA ==="
        end_marker = "=== END STRUCTURED TABLE DATA ==="

        start_idx = enhanced_content.find(start_marker) + len(start_marker)
        end_idx = enhanced_content.find(end_marker)

        if start_idx > len(start_marker) - 1 and end_idx > start_idx:
            json_content = enhanced_content[start_idx:end_idx].strip()

            try:
                parsed_json = json.loads(json_content)
                print("✅ JSON is valid and parseable")
                print(f"✅ Table ID: {parsed_json.get('table_id')}")
                print(f"✅ Title: {parsed_json.get('title')}")
                print(f"✅ Rows: {parsed_json.get('metadata', {}).get('row_count')}")
                print(
                    f"✅ Columns: {parsed_json.get('metadata', {}).get('column_count')}"
                )
                print(f"✅ Headers: {len(parsed_json.get('headers', []))}")
                print(f"✅ Data rows: {len(parsed_json.get('rows', []))}")
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing failed: {e}")
        else:
            print("❌ Could not extract JSON content")
    else:
        print("❌ JSON structure markers not found")

    if "=== SEARCHABLE SUMMARY ===" in enhanced_content:
        print("✅ Searchable summary found")
    else:
        print("❌ Searchable summary not found")

    print("\n📈 EXPECTED USER EXPERIENCE:")
    print("1. User uploads 'Appendix 6 Fee Schedule.pdf'")
    print("2. System detects tables and processes with vision")
    print("3. Table data gets embedded as JSON in document chunks")
    print("4. When user asks about fees, they get citations showing:")
    print("   - Structured JSON with complete table data")
    print("   - All metadata (processing method, dimensions, etc.)")
    print("   - Human-readable summary for context")
    print("5. User can see exactly what data the AI used from the table")

    return enhanced_content


if __name__ == "__main__":
    result = test_json_table_embedding()

    print("\n🎯 SAMPLE CITATION CONTENT (what user will see):")
    print("-" * 60)
    # Show what the user would see in the citation
    lines = result.split("\n")
    citation_start = False
    for line in lines:
        if "=== STRUCTURED TABLE DATA ===" in line:
            citation_start = True
        if citation_start:
            print(line)
        if "=== END SEARCHABLE SUMMARY ===" in line:
            break
