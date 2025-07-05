"""
Test backend model imports for form fields generation
"""

try:
    import sys
    import os

    sys.path.append("backend")

    from backend.app.models import GenerateFormFieldsRequest, GenerateFormFieldsResponse

    print(
        "✅ Successfully imported GenerateFormFieldsRequest and GenerateFormFieldsResponse"
    )

    # Test creating instances
    request = GenerateFormFieldsRequest(description="Test description")
    print(f"✅ Successfully created request: {request}")

    response = GenerateFormFieldsResponse(
        fields=["Field 1", "Field 2"], description_analysis="Test analysis"
    )
    print(f"✅ Successfully created response: {response}")

except Exception as e:
    print(f"❌ Error importing models: {e}")
    import traceback

    traceback.print_exc()
