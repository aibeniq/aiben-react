#!/usr/bin/env python3
"""
Quick test to verify vision analysis makes a difference with NYC PDF
"""
import sys
from test_all_processing_settings import (
    login,
    test_chatbot_kb,
)

session = login()

print("\n" + "=" * 80)
print("Testing vision parameter with NYC PDF (has 14 images)")
print("=" * 80)

# Test with vision ON
print("\n1. Testing with vision_analysis=True:")
result_on, time_on = test_chatbot_kb(session, "vector", True, "enhanced")

# Test with vision OFF
print("\n2. Testing with vision_analysis=False:")
result_off, time_off = test_chatbot_kb(session, "vector", False, "enhanced")

print("\n" + "=" * 80)
print("COMPARISON:")
print("=" * 80)
if result_on and result_off:
    print(f"Vision ON hash:  {result_on['hash']}")
    print(f"Vision OFF hash: {result_off['hash']}")
    print(f"Vision ON length:  {result_on['length']} chars")
    print(f"Vision OFF length: {result_off['length']} chars")

    if result_on["hash"] != result_off["hash"]:
        print("\n✅ SUCCESS: Vision parameter IS making a difference!")
    else:
        print("\n❌ FAIL: Vision parameter NOT making a difference")
        print("This suggests vision analysis may not be affecting chatbot KB queries")
else:
    print("One or both tests failed")
