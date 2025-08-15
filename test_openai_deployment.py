#!/usr/bin/env python3
"""Test script to verify the OpenAI-only deployment configuration is working."""

import requests
import json


def test_system_config():
    """Test the system configuration endpoint."""
    print("=== Testing System Configuration ===")
    try:
        response = requests.get("http://localhost:8000/api/v1/utils/system-config")
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            config = response.json()
            print(f"Configuration: {json.dumps(config, indent=2)}")

            # Verify the expected configuration
            expected_config = {
                "enable_model_selection": False,
                "force_default_llm": "gpt-4o-mini",
                "force_default_embedding": "text-embedding-3-small",
            }

            success = True
            for key, expected_value in expected_config.items():
                actual_value = config.get(key)
                if actual_value != expected_value:
                    print(
                        f"❌ MISMATCH: {key} = {actual_value}, expected {expected_value}"
                    )
                    success = False
                else:
                    print(f"✅ CORRECT: {key} = {actual_value}")

            if success:
                print("\n🎉 All configuration values are correct!")
                print("📋 Expected behavior:")
                print("   - Model Selection tab should be HIDDEN in the frontend")
                print("   - New users should get gpt-4o-mini as default LLM")
                print(
                    "   - New users should get text-embedding-3-small as default embedding"
                )
            else:
                print("\n❌ Configuration issues detected!")
        else:
            print(f"❌ Error: {response.text}")

    except Exception as e:
        print(f"❌ Error connecting to backend: {e}")
        print("🔧 Make sure the backend is running on http://localhost:8000")


def test_frontend_access():
    """Test if the frontend is accessible."""
    print("\n=== Testing Frontend Access ===")
    try:
        response = requests.get("http://localhost", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend is accessible at http://localhost")
            print("📋 Manual verification needed:")
            print("   1. Open http://localhost in your browser")
            print("   2. Log in to the application")
            print("   3. Check the sidebar - 'Model Selection' should NOT be visible")
        else:
            print(f"❌ Frontend returned status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Error accessing frontend: {e}")
        print("🔧 Make sure the frontend is running on http://localhost")


if __name__ == "__main__":
    test_system_config()
    test_frontend_access()

    print("\n" + "=" * 60)
    print("🧪 TESTING SUMMARY")
    print("=" * 60)
    print("✅ Backend system config endpoint tested")
    print("✅ Frontend accessibility tested")
    print("\n📝 To complete verification:")
    print("1. Open http://localhost in browser")
    print("2. Login and check sidebar navigation")
    print("3. Create a new user account")
    print("4. Verify the new user gets correct default models")
    print("=" * 60)
