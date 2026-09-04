#!/usr/bin/env python3
"""Debug script to test the system configuration API and frontend behavior."""

import requests
import json
import time


def test_backend_config():
    """Test the backend system configuration endpoint."""
    print("🔍 TESTING BACKEND SYSTEM CONFIG")
    print("=" * 50)

    try:
        url = "http://localhost:8000/api/v1/utils/system-config"
        print(f"📡 Making request to: {url}")

        response = requests.get(url, timeout=10)
        print(f"📊 Status Code: {response.status_code}")

        if response.status_code == 200:
            config = response.json()
            print(f"📋 Response: {json.dumps(config, indent=2)}")

            # Check the specific values
            enable_model_selection = config.get("enable_model_selection")
            force_default_llm = config.get("force_default_llm")
            force_default_embedding = config.get("force_default_embedding")

            print("\n🔍 ANALYSIS:")
            print(
                f"  enable_model_selection: {enable_model_selection} (type: {type(enable_model_selection)})"
            )
            print(f"  force_default_llm: {force_default_llm}")
            print(f"  force_default_embedding: {force_default_embedding}")

            if enable_model_selection is False:
                print(
                    "✅ Backend correctly configured - model selection SHOULD be hidden"
                )
                return True
            else:
                print(
                    "❌ Backend NOT correctly configured - model selection will be shown"
                )
                print("   Expected: enable_model_selection = false")
                print(f"   Actual: enable_model_selection = {enable_model_selection}")
                return False
        else:
            print(f"❌ Backend returned error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error connecting to backend: {e}")
        return False


def test_frontend_access():
    """Test if the frontend is accessible."""
    print("\n🌐 TESTING FRONTEND ACCESS")
    print("=" * 50)

    try:
        url = "http://localhost"
        print(f"📡 Making request to: {url}")

        response = requests.get(url, timeout=10)
        print(f"📊 Status Code: {response.status_code}")

        if response.status_code == 200:
            print("✅ Frontend is accessible")
            content_preview = (
                response.text[:200] + "..."
                if len(response.text) > 200
                else response.text
            )
            print(f"📄 Content preview: {content_preview}")
            return True
        else:
            print(f"❌ Frontend returned error: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Error accessing frontend: {e}")
        return False


def check_env_file():
    """Check the .env file configuration."""
    print("\n📁 CHECKING .ENV FILE")
    print("=" * 50)

    try:
        with open(".env", "r") as f:
            content = f.read()

        # Look for the specific settings
        lines = content.split("\n")
        relevant_lines = []
        for line in lines:
            if "ENABLE_MODEL_SELECTION" in line or "FORCE_DEFAULT" in line:
                relevant_lines.append(line.strip())

        print("📋 Relevant .env settings:")
        for line in relevant_lines:
            print(f"   {line}")

        # Check if ENABLE_MODEL_SELECTION=false exists
        enable_line = None
        for line in relevant_lines:
            if line.startswith("ENABLE_MODEL_SELECTION="):
                enable_line = line
                break

        if enable_line:
            value = enable_line.split("=")[1]
            print(f"\n🔍 ENABLE_MODEL_SELECTION value: '{value}'")
            if value.lower() == "false":
                print("✅ .env file correctly set to 'false'")
                return True
            else:
                print(
                    f"❌ .env file NOT correctly set. Expected 'false', got '{value}'"
                )
                return False
        else:
            print("❌ ENABLE_MODEL_SELECTION not found in .env file")
            return False

    except Exception as e:
        print(f"❌ Error reading .env file: {e}")
        return False


def main():
    """Run all tests and provide debugging information."""
    print("🚀 DEBUGGING OPENAI-ONLY DEPLOYMENT")
    print("=" * 60)
    print("Testing why Model Selection tab is still visible...")
    print()

    # Test 1: Check .env file
    env_ok = check_env_file()

    # Test 2: Test backend API
    backend_ok = test_backend_config()

    # Test 3: Test frontend access
    frontend_ok = test_frontend_access()

    print("\n" + "=" * 60)
    print("🎯 DEBUGGING SUMMARY")
    print("=" * 60)

    print(f"📁 .env file configuration: {'✅ CORRECT' if env_ok else '❌ INCORRECT'}")
    print(f"🔧 Backend API response: {'✅ CORRECT' if backend_ok else '❌ INCORRECT'}")
    print(
        f"🌐 Frontend accessibility: {'✅ ACCESSIBLE' if frontend_ok else '❌ NOT ACCESSIBLE'}"
    )

    if env_ok and backend_ok and frontend_ok:
        print("\n🤔 ALL BACKEND TESTS PASS - Frontend issue likely:")
        print("   1. Frontend cache not cleared")
        print("   2. useSystemConfig hook not working correctly")
        print("   3. Frontend container needs rebuilding")
        print("\n🔧 SUGGESTED FIXES:")
        print("   1. Clear browser cache and hard refresh")
        print("   2. Rebuild frontend: docker-compose build frontend")
        print("   3. Check browser dev tools for API errors")
    elif not backend_ok:
        print("\n❌ BACKEND ISSUE DETECTED:")
        if not env_ok:
            print("   1. .env file configuration is wrong")
            print("   2. Backend container needs restart to pick up changes")
        else:
            print("   1. Backend not reading .env correctly")
            print("   2. Docker compose not passing environment variables")
        print("\n🔧 SUGGESTED FIXES:")
        print("   1. docker-compose down && docker-compose up -d")
        print("   2. Check backend logs: docker-compose logs backend")
    else:
        print("\n❌ MULTIPLE ISSUES DETECTED - Start with backend fixes first")


if __name__ == "__main__":
    main()
