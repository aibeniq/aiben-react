"""
Test backend imports for form fields generation
"""

try:
    import sys
    import os

    sys.path.append("backend")

    # Test importing the models
    from backend.app.models import GenerateFormFieldsRequest, GenerateFormFieldsResponse

    print("✅ Successfully imported models")

    # Test importing the route
    from backend.app.api.routes.formconnect import router

    print("✅ Successfully imported formconnect router")

    # Test that the endpoint exists
    routes = [route.path for route in router.routes]
    if "/generate-fields" in routes:
        print("✅ Generate fields endpoint found")
    else:
        print("❌ Generate fields endpoint not found")
        print("Available routes:", routes)

    print("🎉 All imports successful!")

except Exception as e:
    print(f"❌ Error importing: {e}")
    import traceback

    traceback.print_exc()
