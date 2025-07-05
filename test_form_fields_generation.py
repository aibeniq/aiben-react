"""
Test the new form fields generation endpoints
"""

import requests
import json


def test_generate_form_fields():
    url = "http://localhost:8001/api/v1/formconnect/generate-fields-json"

    # Test data
    data = {
        "description": "Patient intake form for a medical clinic with demographics, insurance, and medical history",
        "num_fields": 10,
    }

    try:
        response = requests.post(
            url, json=data, headers={"Content-Type": "application/json"}
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"Full Response: {json.dumps(result, indent=2)}")

            fields = result.get("fields", [])
            print(f"\nNumber of fields: {len(fields)}")
            print("Generated Fields:")
            for i, field in enumerate(fields, 1):
                print(f"  {i}. {field}")

            analysis = result.get("description_analysis", "")
            print(f"\nAnalysis: {analysis}")

            return fields
        else:
            print(f"Error Response: {response.text}")
            return None

    except Exception as e:
        print(f"Connection error: {e}")
        return None


if __name__ == "__main__":
    print("Testing Form Fields Generation Endpoint...")
    test_generate_form_fields()
