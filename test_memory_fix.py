#!/usr/bin/env python3
"""
Test script to verify the memory management fix for large knowledge base creation.
This script simulates the conditions that caused the container crash.
"""

import os
import gc
import tempfile
import psutil
from pathlib import Path

# Add the backend directory to Python path
import sys
sys.path.append('/home/ec2-user/aiben-react/backend')

from app.utils.memory_manager import MemoryManager


def create_large_test_file(size_mb: int = 100) -> str:
    """Create a test file of specified size."""
    print(f"Creating {size_mb}MB test file...")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
        # Write random data to simulate a large ZIP file
        chunk_size = 1024 * 1024  # 1MB chunks
        for i in range(size_mb):
            data = os.urandom(chunk_size)
            temp_file.write(data)
            if i % 10 == 0:
                print(f"  Written {i+1}MB...")
        
        temp_file_path = temp_file.name
    
    actual_size = os.path.getsize(temp_file_path) / 1024 / 1024
    print(f"Created test file: {temp_file_path} ({actual_size:.1f}MB)")
    return temp_file_path


def test_memory_safe_reading():
    """Test the memory-safe file reading implementation."""
    print("🧪 Testing Memory-Safe File Reading")
    print("=" * 60)
    
    # Import the fixed functions
    from app.api.routes.knowledgebases import read_file_with_memory_management
    
    # Get initial memory state
    initial_memory = MemoryManager.get_memory_info()
    print(f"Initial memory state:")
    print(f"  Process: {initial_memory['process_memory_mb']:.1f}MB")
    print(f"  System: {initial_memory['system_memory_percent']:.1f}% ({initial_memory['system_available_mb']:.1f}MB available)")
    print()
    
    # Test with different file sizes
    test_sizes = [10, 50, 100, 200]  # MB
    
    for size_mb in test_sizes:
        print(f"📁 Testing {size_mb}MB file...")
        
        # Check if we have enough memory for this test
        memory_check = MemoryManager.check_memory_for_large_file_operation(size_mb, f"{size_mb}MB file test")
        
        if not memory_check['safe']:
            print(f"⚠️  Skipping {size_mb}MB test - insufficient memory")
            print(f"   Current: {memory_check['current_mb']:.1f}MB")
            print(f"   Estimated peak: {memory_check['estimated_peak_mb']:.1f}MB")
            print(f"   Safe limit: {memory_check['safe_limit_mb']:.1f}MB")
            continue
        
        test_file = None
        try:
            # Create test file
            test_file = create_large_test_file(size_mb)
            
            # Record memory before reading
            before_memory = MemoryManager.get_memory_info()
            
            # Test the memory-safe reading
            print(f"  Reading {size_mb}MB file with memory management...")
            data = read_file_with_memory_management(test_file)
            
            # Record memory after reading
            after_memory = MemoryManager.get_memory_info()
            
            # Calculate memory usage
            memory_increase = after_memory['process_memory_mb'] - before_memory['process_memory_mb']
            peak_usage_ratio = memory_increase / size_mb if size_mb > 0 else 0
            
            print(f"  ✅ Success! Read {len(data) // 1024 // 1024}MB")
            print(f"  📊 Memory impact:")
            print(f"     Before: {before_memory['process_memory_mb']:.1f}MB")
            print(f"     After: {after_memory['process_memory_mb']:.1f}MB")
            print(f"     Increase: {memory_increase:.1f}MB")
            print(f"     Ratio: {peak_usage_ratio:.2f}x file size")
            print(f"     System usage: {after_memory['system_memory_percent']:.1f}%")
            
            # Good memory usage should be close to 1x file size, not 2x+
            if peak_usage_ratio < 1.5:
                print(f"  🎉 Excellent memory efficiency!")
            elif peak_usage_ratio < 2.0:
                print(f"  ✅ Good memory efficiency")
            else:
                print(f"  ⚠️  High memory usage - may need optimization")
            
            # Clean up the data to free memory
            del data
            gc.collect()
            
        except Exception as e:
            print(f"  ❌ Error reading {size_mb}MB file: {e}")
            
        finally:
            # Clean up test file
            if test_file and os.path.exists(test_file):
                try:
                    os.unlink(test_file)
                    print(f"  🗑️  Cleaned up test file")
                except Exception as e:
                    print(f"  ⚠️  Could not clean up test file: {e}")
        
        print()
        
        # Force garbage collection between tests
        gc.collect()
    
    # Final memory state
    final_memory = MemoryManager.get_memory_info()
    print(f"Final memory state:")
    print(f"  Process: {final_memory['process_memory_mb']:.1f}MB")
    print(f"  System: {final_memory['system_memory_percent']:.1f}% ({final_memory['system_available_mb']:.1f}MB available)")
    
    memory_delta = final_memory['process_memory_mb'] - initial_memory['process_memory_mb']
    if memory_delta < 50:  # Less than 50MB increase is acceptable
        print(f"  🎉 Memory leak test passed! Delta: {memory_delta:.1f}MB")
    else:
        print(f"  ⚠️  Potential memory leak detected! Delta: {memory_delta:.1f}MB")


def test_memory_monitoring():
    """Test the memory monitoring utilities."""
    print("🔍 Testing Memory Monitoring")
    print("=" * 40)
    
    # Test memory info
    memory_info = MemoryManager.get_memory_info()
    print(f"Memory Info:")
    for key, value in memory_info.items():
        if 'mb' in key:
            print(f"  {key}: {value:.1f}MB")
        else:
            print(f"  {key}: {value:.1f}%")
    
    print()
    
    # Test memory check for large operations
    test_sizes = [100, 500, 1000]  # MB
    for size in test_sizes:
        check_result = MemoryManager.check_memory_for_large_file_operation(size, f"{size}MB operation")
        status = "✅ SAFE" if check_result['safe'] else "⚠️  RISKY"
        print(f"{size}MB operation: {status}")
        print(f"  Estimated peak: {check_result['estimated_peak_mb']:.1f}MB")
        print(f"  Safe limit: {check_result['safe_limit_mb']:.1f}MB")
        print()


if __name__ == "__main__":
    print("🚀 Knowledge Base Memory Management Fix Test")
    print("=" * 80)
    print()
    
    try:
        test_memory_monitoring()
        print()
        test_memory_safe_reading()
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    print("✅ Test completed!")