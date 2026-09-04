#!/usr/bin/env python3
"""
Test script to validate the VisionService method call fixes.
"""

import sys
from pathlib import Path

# Add the backend directory to the path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))


def test_vision_method_calls():
    """Test if VisionService method calls are correctly formatted."""

    print("🔧 Testing VisionService Method Call Fixes")
    print("=" * 50)

    # Check if we can import VisionService without errors
    try:
        from app.services.vision_service import VisionService

        print("✅ VisionService import successful")

        # Check method signatures
        import inspect

        # Check process_images_with_prompt signature
        sig = inspect.signature(VisionService.process_images_with_prompt)
        params = list(sig.parameters.keys())
        expected_params = ["llm", "images", "prompt_template", "variables", "context"]

        print(f"📋 process_images_with_prompt parameters: {params}")

        if all(param in params for param in expected_params[:4]):  # context is optional
            print("✅ process_images_with_prompt has correct parameters")
        else:
            print("❌ process_images_with_prompt parameters don't match expected")
            return False

        # Check safe_vision_analysis signature
        sig = inspect.signature(VisionService.safe_vision_analysis)
        params = list(sig.parameters.keys())
        expected_params = ["llm", "prompt_template", "variables", "images"]

        print(f"📋 safe_vision_analysis parameters: {params}")

        if all(param in params for param in expected_params):
            print("✅ safe_vision_analysis has correct parameters")
        else:
            print("❌ safe_vision_analysis parameters don't match expected")
            return False

        return True

    except Exception as e:
        print(f"❌ VisionService import failed: {e}")
        return False


def test_method_call_syntax():
    """Test if the method calls in routes use correct syntax."""

    print("\n🔧 Testing Method Call Syntax in Routes")
    print("=" * 50)

    # Files to check
    route_files = [
        "backend/app/api/routes/chatbot.py",
        "backend/app/api/routes/formconnect.py",
        "backend/app/api/routes/twincheck.py",
        "backend/app/api/routes/veradoc.py",
    ]

    issues_found = []

    for route_file in route_files:
        route_path = Path(__file__).parent / route_file
        if route_path.exists():
            with open(route_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Check for old-style method calls (positional arguments)
            if "VisionService.process_images_with_prompt(" in content:
                # Look for calls without named parameters
                lines = content.split("\n")
                for i, line in enumerate(lines, 1):
                    if "VisionService.process_images_with_prompt(" in line:
                        # Check if the call uses named parameters
                        if "llm=" not in line and "images=" not in line:
                            issues_found.append(
                                f"{route_file}:{i} - Missing named parameters"
                            )

            # Check for calls with old 'prompt' parameter
            if "prompt=" in content and "VisionService" in content:
                lines = content.split("\n")
                for i, line in enumerate(lines, 1):
                    if "prompt=" in line and "VisionService" in line:
                        issues_found.append(
                            f"{route_file}:{i} - Using deprecated 'prompt' parameter"
                        )

            print(f"📋 Checked {route_file}")
        else:
            print(f"⚠️  {route_file} not found")

    if issues_found:
        print("\n❌ Issues found:")
        for issue in issues_found:
            print(f"   {issue}")
        return False
    else:
        print("\n✅ All method calls use correct syntax")
        return True


def main():
    """Run all tests."""
    print("🚀 VisionService Fix Validation")
    print("=" * 50)

    tests = [
        ("VisionService Method Signatures", test_vision_method_calls),
        ("Route Method Call Syntax", test_method_call_syntax),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n🔧 {test_name}")
        print("-" * 30)
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")

    print("\n" + "=" * 50)
    print(f"📊 Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All VisionService fixes validated successfully!")
        print("💡 You can now test with image-only PDFs in chatbot vector search mode.")
        return 0
    else:
        print("❌ Some issues remain. Please check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
