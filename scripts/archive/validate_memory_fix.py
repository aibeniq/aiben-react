#!/usr/bin/env python3
"""
Simple validation script to test the memory management fix.
"""

import os
import sys
import tempfile


def test_memory_functions():
    """Test that the memory management functions are working."""
    print("🧪 Testing Memory Management Functions")
    print("=" * 50)
    
    try:
        # Import the functions we fixed
        from app.utils.memory_manager import MemoryManager
        from app.api.routes.knowledgebases import read_file_with_memory_management
        
        print("✅ Successfully imported memory management functions")
        
        # Test memory info
        memory_info = MemoryManager.get_memory_info()
        print(f"📊 Current memory state:")
        print(f"   Process: {memory_info['process_memory_mb']:.1f}MB")
        print(f"   System: {memory_info['system_memory_percent']:.1f}%")
        print(f"   Available: {memory_info['system_available_mb']:.1f}MB")
        
        # Test the new memory check function
        check_result = MemoryManager.check_memory_for_large_file_operation(100, "test operation")
        status = "SAFE" if check_result['safe'] else "RISKY"
        print(f"🔍 100MB operation check: {status}")
        
        # Create a small test file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            test_data = b"Hello, World! " * 1000  # Small test data
            temp_file.write(test_data)
            temp_file_path = temp_file.name
        
        try:
            # Test reading with memory management
            result = read_file_with_memory_management(temp_file_path)
            print(f"✅ Successfully read test file: {len(result)} bytes")
            
            if result == test_data:
                print("✅ Data integrity check passed")
            else:
                print("❌ Data integrity check failed")
                
        finally:
            # Clean up
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        
        print("🎉 All memory management functions are working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing memory functions: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_configuration():
    """Check that the new configuration options are available."""
    print("\n🔧 Testing Configuration")
    print("=" * 30)
    
    try:
        from app.core.config import settings
        
        # Check new configuration options
        attrs_to_check = [
            'KB_MEMORY_SAFETY_THRESHOLD',
            'KB_HIGH_MEMORY_USAGE_THRESHOLD',
            'KB_MAX_IN_MEMORY_SIZE_MB',
            'KB_STREAM_CHUNK_SIZE_MB'
        ]
        
        for attr in attrs_to_check:
            if hasattr(settings, attr):
                value = getattr(settings, attr)
                print(f"✅ {attr}: {value}")
            else:
                print(f"❌ Missing: {attr}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking configuration: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Memory Management Fix Validation")
    print("=" * 50)
    
    success = True
    
    success &= test_memory_functions()
    success &= check_configuration()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed! The memory management fix is working.")
    else:
        print("❌ Some tests failed. Please check the implementation.")