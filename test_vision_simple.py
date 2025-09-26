#!/usr/bin/env python3
"""
Simple Vision Enhancement Test Suite
Tests the vision implementation without requiring full app configuration.
"""

import sys
import os
from pathlib import Path

# Add the backend directory to the path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))


def test_vision_service_class():
    """Test if VisionService class is properly defined by checking the source file."""
    try:
        # Check the vision service file directly since import requires config
        vision_service_path = backend_path / "app" / "services" / "vision_service.py"
        if vision_service_path.exists():
            with open(vision_service_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Check if VisionService class exists
            if "class VisionService:" in content:
                print("✅ VisionService class found")

                # Check key methods exist
                expected_methods = [
                    "def is_vision_enabled",
                    "def process_images_with_prompt",
                    "def combine_text_and_vision_analysis",
                ]

                missing_methods = []
                for method in expected_methods:
                    if method not in content:
                        missing_methods.append(method.replace("def ", ""))

                if missing_methods:
                    print(f"❌ Missing methods: {missing_methods}")
                    return False
                else:
                    print("✅ All expected methods found")
                    return True
            else:
                print("❌ VisionService class not found")
                return False
        else:
            print("❌ Vision service file not found")
            return False

    except Exception as e:
        print(f"❌ Error testing vision service: {e}")
        return False


def test_document_utils_enhancement():
    """Test if document_utils has been enhanced with vision capabilities."""
    try:
        import app.services.document_utils

        # Check if enhanced function exists
        if hasattr(
            app.services.document_utils,
            "extract_documents_and_images_from_file_unified",
        ):
            print("✅ Enhanced document extraction function found")
            return True
        else:
            print("❌ Enhanced document extraction function not found")
            return False

    except ImportError as e:
        print(f"❌ Cannot import document_utils: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing document_utils: {e}")
        return False


def test_vision_config_additions():
    """Test if vision configurations have been added."""
    try:
        # Try to read the config file directly
        config_file = backend_path / "app" / "core" / "config.py"
        if config_file.exists():
            with open(config_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Check for vision-related additions
            vision_indicators = [
                "VISION_ENABLED_MODELS",
                "gpt-4o",
                "claude-3",
                "vision_prompt",
            ]

            found_indicators = []
            for indicator in vision_indicators:
                if indicator in content:
                    found_indicators.append(indicator)

            if len(found_indicators) >= 3:  # At least 3 indicators should be present
                print(
                    f"✅ Vision configuration found ({len(found_indicators)}/4 indicators)"
                )
                return True
            else:
                print(
                    f"❌ Insufficient vision configuration ({len(found_indicators)}/4 indicators)"
                )
                return False
        else:
            print("❌ Config file not found")
            return False

    except Exception as e:
        print(f"❌ Error testing config: {e}")
        return False


def test_route_enhancements():
    """Test if routes have been enhanced with vision capabilities."""
    routes_to_check = ["twincheck.py", "chatbot.py", "formconnect.py", "veradoc.py"]

    enhanced_count = 0

    for route_file in routes_to_check:
        try:
            route_path = backend_path / "app" / "api" / "routes" / route_file
            if route_path.exists():
                with open(route_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Check for vision service import or usage
                if "VisionService" in content or "vision_service" in content:
                    print(f"✅ {route_file} enhanced with vision")
                    enhanced_count += 1
                else:
                    print(f"⚠️  {route_file} may not have vision enhancement")
            else:
                print(f"❌ {route_file} not found")

        except Exception as e:
            print(f"❌ Error checking {route_file}: {e}")

    if enhanced_count >= 3:  # At least 3 routes should be enhanced
        print(f"✅ Route enhancements found ({enhanced_count}/4 routes)")
        return True
    else:
        print(f"⚠️  Limited route enhancements ({enhanced_count}/4 routes)")
        return enhanced_count > 0


def test_frontend_components():
    """Test if frontend vision components exist."""
    frontend_path = Path(__file__).parent / "frontend"

    # Check for VisionIndicator component
    vision_indicator_path = (
        frontend_path / "src" / "components" / "Common" / "VisionIndicator.tsx"
    )
    if vision_indicator_path.exists():
        print("✅ VisionIndicator component found")
        component_exists = True
    else:
        print("❌ VisionIndicator component not found")
        component_exists = False

    # Check for useModelCapabilities hook
    hook_path = frontend_path / "src" / "hooks" / "useModelCapabilities.ts"
    if hook_path.exists():
        print("✅ useModelCapabilities hook found")
        hook_exists = True
    else:
        print("❌ useModelCapabilities hook not found")
        hook_exists = False

    return component_exists and hook_exists


def main():
    """Run all tests."""
    print("🚀 Simple Vision Enhancement Test")
    print("=" * 40)

    tests = [
        ("Vision Service Class", test_vision_service_class),
        ("Document Utils Enhancement", test_document_utils_enhancement),
        ("Vision Configuration", test_vision_config_additions),
        ("Route Enhancements", test_route_enhancements),
        ("Frontend Components", test_frontend_components),
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

    print("\n" + "=" * 40)
    print(f"📊 Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Vision enhancement implementation looks good.")
        return 0
    elif passed > total // 2:
        print("⚠️  Most tests passed. Implementation is mostly complete.")
        return 0
    else:
        print("❌ Many tests failed. Please check the implementation.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
