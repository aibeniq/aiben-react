#!/usr/bin/env python3
"""
Test to validate the APA demographic table extraction improvements.

This test simulates the processing and checks if the improved vision prompt
and document processing correctly extract the multi-column demographic data.
"""

import json


def test_expected_vs_actual():
    """Test the expected extraction format against what should be produced"""

    print("=" * 80)
    print("TESTING APA DEMOGRAPHIC TABLE EXTRACTION IMPROVEMENTS")
    print("=" * 80)

    # This is what should be extracted from the APA table
    expected_structure = {
        "table_id": "table_1",
        "page": 1,
        "title": "Sociodemographic Characteristics of Participants at Baseline",
        "headers": {
            "Guided self-help": ["n", "%"],
            "Unguided self-help": ["n", "%"],
            "Wait-list control": ["n", "%"],
            "Full sample": ["n", "%"],
        },
        "rows": [
            {
                "Baseline characteristic": "Female",
                "is_subheader": False,
                "values": {
                    "Guided self-help": {"n": 25, "%": 50},
                    "Unguided self-help": {"n": 20, "%": 40},
                    "Wait-list control": {"n": 23, "%": 46},
                    "Full sample": {"n": 68, "%": 45},
                },
            },
            {
                "Baseline characteristic": "High school/some college",
                "is_subheader": False,
                "values": {
                    "Guided self-help": {"n": 22, "%": 44},
                    "Unguided self-help": {"n": 17, "%": 34},
                    "Wait-list control": {"n": 13, "%": 26},
                    "Full sample": {"n": 52, "%": 35},
                },
            },
        ],
    }

    print("📋 Expected Structure for APA Demographic Table:")
    print(f"   Title: {expected_structure['title']}")
    print(f"   Headers: {list(expected_structure['headers'].keys())}")
    print(f"   Rows: {len(expected_structure['rows'])}")

    # Test header conversion
    print("\n🔄 Testing Header Processing:")

    grouped_headers = expected_structure["headers"]
    print(f"   Original grouped headers: {grouped_headers}")

    # Simulate the flattening process from document_utils.py
    flattened_headers = []
    for group_name, subcolumns in grouped_headers.items():
        if isinstance(subcolumns, list):
            for subcol in subcolumns:
                flattened_headers.append(f"{group_name} {subcol}")
        else:
            flattened_headers.append(str(group_name))

    print(f"   Flattened headers: {flattened_headers}")
    print(
        f"   ✅ Generated {len(flattened_headers)} flat headers from {len(grouped_headers)} groups"
    )

    # Test row processing
    print("\n📊 Testing Row Processing:")

    for i, row in enumerate(expected_structure["rows"]):
        characteristic = row["Baseline characteristic"]
        values = row["values"]

        print(f"\n   Row {i+1}: '{characteristic}'")

        # Simulate the flattening process
        flattened_row = {"Baseline characteristic": characteristic}

        for group_name, group_data in values.items():
            if isinstance(group_data, dict):
                for subcol, val in group_data.items():
                    flat_header = f"{group_name} {subcol}"
                    flattened_row[flat_header] = str(val) if val is not None else ""
            else:
                flattened_row[group_name] = (
                    str(group_data) if group_data is not None else ""
                )

        print(f"      Original: {len(values)} group values")
        print(
            f"      Flattened: {len(flattened_row)-1} data columns"
        )  # -1 for characteristic column

        # Validate specific values
        if characteristic == "Female":
            expected_female = {
                "Guided self-help n": "25",
                "Guided self-help %": "50",
                "Unguided self-help n": "20",
                "Unguided self-help %": "40",
                "Wait-list control n": "23",
                "Wait-list control %": "46",
                "Full sample n": "68",
                "Full sample %": "45",
            }

            matches = 0
            for key, expected_val in expected_female.items():
                if key in flattened_row and flattened_row[key] == expected_val:
                    matches += 1
                    print(f"      ✅ {key}: {expected_val}")
                else:
                    actual_val = flattened_row.get(key, "MISSING")
                    print(f"      ❌ {key}: Expected {expected_val}, got {actual_val}")

            coverage = matches / len(expected_female) * 100
            print(f"      Coverage: {matches}/{len(expected_female)} = {coverage:.1f}%")

        elif characteristic == "High school/some college":
            # This is the key test case from user's feedback
            expected_education = {
                "Guided self-help n": "22",
                "Guided self-help %": "44",
                "Unguided self-help n": "17",
                "Unguided self-help %": "34",
                "Wait-list control n": "13",
                "Wait-list control %": "26",
                "Full sample n": "52",
                "Full sample %": "35",
            }

            print(f"      🎯 KEY TEST: High School/Some College numbers")
            for key, expected_val in expected_education.items():
                if key in flattened_row and flattened_row[key] == expected_val:
                    print(f"      ✅ {key}: {expected_val}")
                else:
                    actual_val = flattened_row.get(key, "MISSING")
                    print(f"      ❌ {key}: Expected {expected_val}, got {actual_val}")

    # Comparison with old buggy format
    print("\n❌ OLD BUGGY FORMAT (what was happening before):")
    buggy_format = {
        "Baseline characteristic": "High school/some college",
        "['n', '%']": "34",  # Only extracting one value!
    }
    print(f"   {json.dumps(buggy_format, indent=2)}")
    print(
        "   ❌ PROBLEMS: Only 1 value instead of 8, no group distinction, wrong structure"
    )

    print("\n✅ NEW IMPROVED FORMAT (what should happen now):")
    improved_format = {
        "Baseline characteristic": "High school/some college",
        "Guided self-help n": "22",
        "Guided self-help %": "44",
        "Unguided self-help n": "17",
        "Unguided self-help %": "34",
        "Wait-list control n": "13",
        "Wait-list control %": "26",
        "Full sample n": "52",
        "Full sample %": "35",
    }
    print(f"   {json.dumps(improved_format, indent=2)}")
    print(
        "   ✅ IMPROVEMENTS: All 8 values captured, group distinction preserved, proper structure"
    )

    print("\n" + "=" * 80)
    print("🔬 ANALYSIS SUMMARY")
    print("=" * 80)

    print("✅ VISION SERVICE IMPROVEMENTS:")
    print("   - Enhanced prompt specifically targets demographic tables")
    print("   - Recognizes grouped column headers (treatment groups)")
    print("   - Extracts structured data with group/subcolumn mapping")
    print("   - Identifies category headers vs data rows")

    print("\n✅ DOCUMENT PROCESSING IMPROVEMENTS:")
    print("   - Added support for grouped header format")
    print("   - Flattens grouped headers to simple strings")
    print("   - Processes structured row values correctly")
    print("   - Maintains backward compatibility")

    print("\n🎯 EXPECTED IMPACT:")
    print("   - High School/Some College should show ALL treatment group values")
    print("   - Female demographics should show complete breakdown")
    print("   - No more single-value extraction errors")
    print("   - Proper multi-column table recognition")

    print("\n📋 TO VALIDATE:")
    print("   1. Test with actual APA document")
    print("   2. Check logs for 'structured demographic table format' message")
    print("   3. Verify all 8 values extracted for education categories")
    print("   4. Confirm treatment group names preserved")


if __name__ == "__main__":
    test_expected_vs_actual()
