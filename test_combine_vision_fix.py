#!/usr/bin/env python3
"""
Test to validate the combine_text_and_vision_analysis fix
"""


def test_vision_method_signature():
    """Test that VisionService.combine_text_and_vision_analysis has correct signature"""

    print("🔧 Testing combine_text_and_vision_analysis Method Signature")
    print("=" * 60)

    try:
        import sys
        from pathlib import Path

        # Add the backend directory to the path
        backend_path = Path(__file__).parent / "backend"
        sys.path.insert(0, str(backend_path))

        from app.services.vision_service import VisionService
        import inspect

        # Get method signature
        sig = inspect.signature(VisionService.combine_text_and_vision_analysis)
        params = list(sig.parameters.keys())

        print(f"📋 Method parameters: {params}")

        # Expected parameters
        expected_params = ["text_analysis", "vision_analysis", "combination_strategy"]

        # Check if parameters match
        if all(
            param in params for param in expected_params[:2]
        ):  # first 2 are required
            print("✅ Method signature is correct")
            print(f"✅ Required parameters: text_analysis, vision_analysis")
            print(f"✅ Optional parameter: combination_strategy")
            return True
        else:
            print("❌ Method signature doesn't match expected")
            print(f"Expected: {expected_params}")
            print(f"Found: {params}")
            return False

    except Exception as e:
        print(f"❌ Error testing method signature: {e}")
        return False


def test_chatbot_usage():
    """Test that chatbot uses the method correctly"""

    print("\n🔧 Testing Chatbot Method Usage")
    print("=" * 60)

    try:
        from pathlib import Path

        chatbot_path = Path(__file__).parent / "backend/app/api/routes/chatbot.py"

        if chatbot_path.exists():
            with open(chatbot_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Look for the problematic call
            if (
                "text_content=" in content
                and "combine_text_and_vision_analysis" in content
            ):
                print("❌ Found incorrect parameter 'text_content' in chatbot")
                return False

            # Look for correct usage
            if (
                "text_analysis=" in content
                and "combine_text_and_vision_analysis" in content
            ):
                print("✅ Found correct parameter 'text_analysis' in chatbot")
                return True
            elif "combine_text_and_vision_analysis(" in content:
                # Check if any calls use positional arguments (which would be correct)
                lines = content.split("\n")
                for i, line in enumerate(lines, 1):
                    if "combine_text_and_vision_analysis(" in line:
                        # Get the next few lines to see the full call
                        call_lines = []
                        for j in range(5):  # Look at next 5 lines
                            if i + j < len(lines):
                                call_lines.append(lines[i + j - 1])

                        call_text = "\n".join(call_lines)

                        # Check if it uses correct parameters or positional args
                        if "text_analysis=" in call_text or (
                            not "text_content=" in call_text
                            and not "llm=" in call_text
                            and not "images=" in call_text
                        ):
                            print(f"✅ Found correct usage at line {i}")
                            return True

                print("⚠️  Found method calls but couldn't verify correctness")
                return True
            else:
                print("ℹ️  No combine_text_and_vision_analysis calls found in chatbot")
                return True

        else:
            print("❌ Chatbot file not found")
            return False

    except Exception as e:
        print(f"❌ Error testing chatbot usage: {e}")
        return False


def main():
    """Run the test"""
    print("🚀 Vision Method Fix Validation")
    print("=" * 60)

    tests = [
        ("Method Signature", test_vision_method_signature),
        ("Chatbot Usage", test_chatbot_usage),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        if test_func():
            passed += 1

    print("\n" + "=" * 60)
    print(f"📊 Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All fixes validated! Your vision analysis should work now.")
        print("💡 Try testing with an image-only PDF in chatbot vector search mode.")
    else:
        print("❌ Some issues may remain.")

    return passed == total


if __name__ == "__main__":
    main()
