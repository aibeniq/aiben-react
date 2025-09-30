#!/usr/bin/env python3
"""
Test script to verify template formatting fixes in LLM service.
This script tests the invoke_llm function with various scenarios that previously caused errors.
"""

import sys
import os
import json

# Add the backend app to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_template_formatting_fixes():
    """Test various scenarios that previously caused template formatting errors."""
    
    print("🧪 Testing template formatting fixes...")
    
    try:
        from app.services.llms import invoke_llm
    except ImportError as e:
        print(f"❌ Could not import invoke_llm: {e}")
        return False
    
    # Test case 1: Empty variables dict (was causing issues)
    print("\n📝 Test 1: Empty variables dict")
    try:
        # Simulate text with JSON metadata that was causing KeyError
        prompt_with_metadata = """
        Extract the provider name from this text:
        
        Table: Provider Information
        {
          "_table_metadata": {
            "table_id": "provider_info_001",
            "extraction_method": "table_detection"
          },
          "content": "ABC Medical Center - Dr. John Smith"
        }
        
        Please extract just the provider name.
        """
        
        result = invoke_llm(
            prompt=prompt_with_metadata,
            variables={},  # Empty dict that was causing issues
            llm_provider="openai",
            llm_model="gpt-4o-mini"
        )
        print("✅ Test 1 PASSED: Empty variables dict handled correctly")
        print(f"   Result length: {len(str(result))}")
        
    except Exception as e:
        print(f"❌ Test 1 FAILED: {e}")
        return False
    
    # Test case 2: Variables dict with actual content
    print("\n📝 Test 2: Variables dict with content")
    try:
        prompt_template = "Extract the {field_type} from this document: {document_text}"
        variables = {
            "field_type": "provider name",
            "document_text": "Medical Center ABC, Dr. Jane Doe"
        }
        
        result = invoke_llm(
            prompt=prompt_template,
            variables=variables,
            llm_provider="openai", 
            llm_model="gpt-4o-mini"
        )
        print("✅ Test 2 PASSED: Variables dict with content handled correctly")
        print(f"   Result length: {len(str(result))}")
        
    except Exception as e:
        print(f"❌ Test 2 FAILED: {e}")
        return False
    
    # Test case 3: Text with curly braces that shouldn't be template formatted
    print("\n📝 Test 3: Text with curly braces (no variables)")
    try:
        prompt_with_braces = """
        Process this JSON data:
        {
          "provider": "Health System XYZ",
          "npi": "1234567890",
          "address": {"street": "123 Main St", "city": "Anytown"}
        }
        Extract the provider name.
        """
        
        result = invoke_llm(
            prompt=prompt_with_braces,
            variables={},  # Empty - should not trigger template formatting
            llm_provider="openai",
            llm_model="gpt-4o-mini"
        )
        print("✅ Test 3 PASSED: Curly braces in text handled correctly")
        print(f"   Result length: {len(str(result))}")
        
    except Exception as e:
        print(f"❌ Test 3 FAILED: {e}")
        return False
    
    print("\n🎉 All template formatting tests PASSED!")
    print("   The template formatting fixes are working correctly.")
    return True

def test_additional_llm_functions():
    """Test other LLM functions that were also fixed."""
    
    print("\n🧪 Testing additional LLM functions...")
    
    try:
        from app.services.llms import invoke_llm_with_image
        print("✅ invoke_llm_with_image import successful")
    except ImportError as e:
        print(f"❌ Could not import invoke_llm_with_image: {e}")
        return False
    
    # We won't actually call invoke_llm_with_image without proper image data,
    # but we can verify the import works
    print("✅ Additional LLM function imports successful")
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("🔍 FormConnect Template Formatting Fix Verification")
    print("=" * 60)
    
    # Test basic template formatting fixes
    test1_passed = test_template_formatting_fixes()
    
    # Test additional functions
    test2_passed = test_additional_llm_functions()
    
    print("\n" + "=" * 60)
    if test1_passed and test2_passed:
        print("✅ ALL TESTS PASSED!")
        print("   Template formatting fixes are working correctly.")
        print("   FormConnect should now work without template errors.")
    else:
        print("❌ SOME TESTS FAILED!")
        print("   Please check the error messages above.")
    print("=" * 60)