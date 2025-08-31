#!/usr/bin/env python3
"""
Test script to verify UV cache directory fix.
"""

import os
import subprocess
import sys
import tempfile


def test_uv_cache_fix():
    print("=== Testing UV Cache Directory Fix ===")

    # Set UV cache to a writable location
    original_env = os.environ.copy()
    test_env = os.environ.copy()
    test_env["UV_CACHE_DIR"] = tempfile.gettempdir() + "/uv-cache"

    print(f"Original UV_CACHE_DIR: {original_env.get('UV_CACHE_DIR', 'Not set')}")
    print(f"Test UV_CACHE_DIR: {test_env['UV_CACHE_DIR']}")

    # Test if uv is available
    try:
        result = subprocess.run(
            ["uv", "--version"], capture_output=True, text=True, env=test_env
        )
        print(f"UV version: {result.stdout.strip()}")

        # Test if the cache directory can be created
        cache_dir = test_env["UV_CACHE_DIR"]
        os.makedirs(cache_dir, exist_ok=True)
        print(f"✅ Cache directory created successfully: {cache_dir}")

        # Test a simple uv command
        result = subprocess.run(
            ["uv", "pip", "list"],
            capture_output=True,
            text=True,
            env=test_env,
            timeout=30,
        )

        if result.returncode == 0:
            print("✅ UV pip list command successful")
        else:
            print(f"❌ UV pip list failed: {result.stderr}")

    except FileNotFoundError:
        print("❌ UV not found")
    except subprocess.TimeoutExpired:
        print("⚠️ UV command timed out")
    except Exception as e:
        print(f"❌ Error testing UV: {e}")


if __name__ == "__main__":
    test_uv_cache_fix()
