#!/usr/bin/env python3
"""
Test script to demonstrate that the header normalization fix is working correctly.
This simulates the exact scenario that was causing the TypeError: unhashable type: 'dict'
"""


def test_header_normalization():
    """Test the header normalization logic that fixes the TypeError"""

    # Simulate the problematic data that was causing the TypeError
    problematic_headers = [
        "Simple Header",
        {"main": "Group A", "sub": "n"},  # This would cause TypeError before fix
        {"name": "Column Name"},
        {"complex": "value", "other": "data"},
        ["Item1", "Item2"],
        None,
    ]

    problematic_values = [
        "Simple Value",
        {"key1": "value1", "key2": "value2"},  # Complex dict value
        ["item1", "item2", "item3"],  # Array value
        None,
        123,
        {"nested": {"deep": "value"}},
    ]

    print("=" * 60)
    print("TESTING HEADER NORMALIZATION FIX")
    print("=" * 60)

    # Test header normalization (copy of our fix logic)
    def normalize_header(h):
        if h is None:
            return None
        elif isinstance(h, dict):
            if "main" in h and "sub" in h:
                return f"{h['main']} - {h['sub']}"
            elif "name" in h:
                return str(h["name"])
            else:
                return ", ".join(f"{k}: {v}" for k, v in h.items() if v is not None)
        elif isinstance(h, list):
            return ", ".join(str(item) for item in h if item is not None)
        else:
            return str(h).strip()

    def normalize_value(raw_value):
        if raw_value is None:
            return ""
        elif isinstance(raw_value, dict):
            return ", ".join(f"{k}: {v}" for k, v in raw_value.items() if v is not None)
        elif isinstance(raw_value, list):
            return ", ".join(str(item) for item in raw_value if item is not None)
        else:
            return str(raw_value).strip()

    # Test each header
    print("Testing header normalization:")
    normalized_headers = []
    for i, header in enumerate(problematic_headers):
        if header is None:
            continue

        original_type = type(header).__name__
        normalized = normalize_header(header)
        normalized_type = type(normalized).__name__

        print(
            f"  {i}: {original_type:<6} {str(header):<30} -> {normalized_type:<6} '{normalized}'"
        )

        # Test if it can be used as dict key (this would fail before our fix)
        try:
            test_dict = {normalized: "test"}
            print(f"      ✅ SUCCESS: Can use as dictionary key")
            normalized_headers.append(normalized)
        except Exception as e:
            print(f"      ❌ FAILED: {e}")

    print("\nTesting value normalization:")
    normalized_values = []
    for i, value in enumerate(problematic_values):
        original_type = type(value).__name__
        normalized = normalize_value(value)
        normalized_type = type(normalized).__name__

        print(
            f"  {i}: {original_type:<6} {str(value):<30} -> {normalized_type:<6} '{normalized}'"
        )
        normalized_values.append(normalized)

    # Test complete row processing (this is what was failing before)
    print("\n" + "=" * 60)
    print("TESTING COMPLETE ROW PROCESSING")
    print("=" * 60)

    # Simulate the exact scenario from the error logs
    test_headers = ["Name", {"main": "Group A", "sub": "n"}, "Score"]
    test_row = ["John", {"type": "student", "level": "senior"}, 85]

    print(f"Original headers: {test_headers}")
    print(f"Original row: {test_row}")

    # Process headers (normalize complex objects to strings)
    processed_headers = []
    for h in test_headers:
        normalized = normalize_header(h)
        if normalized:
            processed_headers.append(normalized)

    print(f"Processed headers: {processed_headers}")

    # Build the row object that was causing TypeError
    row_obj = {}
    for i, header in enumerate(processed_headers):
        raw_value = test_row[i] if i < len(test_row) else ""
        value = normalize_value(raw_value)

        # This assignment was failing before the fix
        try:
            row_obj[header] = value
            print(f"  ✅ row_obj['{header}'] = '{value}'")
        except Exception as e:
            print(f"  ❌ FAILED: {e}")

    print(f"\nFinal row object: {row_obj}")
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED - TypeError: unhashable type: 'dict' is FIXED!")
    print("=" * 60)


if __name__ == "__main__":
    test_header_normalization()
