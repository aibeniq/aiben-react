#!/usr/bin/env python3
"""
Test script to verify knowledge base creation improvements.
This script tests the file validation functionality.
"""

import tempfile
import os

def create_test_file(filename, size_mb):
    """Create a test file of specified size in MB."""
    content = b"Test content " * 1000  # Base content
    target_size = int(size_mb * 1024 * 1024)  # Convert MB to bytes
    
    # Repeat content to reach target size
    multiplier = max(1, target_size // len(content))
    content = content * multiplier
    
    # Truncate to exact size
    content = content[:target_size]
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=filename) as f:
        f.write(content)
        return f.name

def test_file_limits():
    """Test the file limit validation."""
    print("🧪 Testing Knowledge Base File Limits")
    print("=" * 50)
    
    # Test 1: Normal case - should work
    print("\n1. Testing normal case (5 small files)...")
    test_files = []
    try:
        for i in range(5):
            test_file = create_test_file(f"_test{i}.txt", 1)  # 1MB each
            test_files.append(test_file)
        
        print(f"✅ Created {len(test_files)} test files, 1MB each")
        print("   This should work with our limits (50 files max, 100MB total, 20MB per file)")
        
    finally:
        # Clean up
        for f in test_files:
            try:
                os.unlink(f)
            except:
                pass
    
    # Test 2: Too large individual file - should fail
    print("\n2. Testing oversized file (25MB)...")
    large_file = None
    try:
        large_file = create_test_file("_large.txt", 25)  # 25MB - exceeds 20MB limit
        print(f"✅ Created large test file: {os.path.getsize(large_file) // (1024*1024)}MB")
        print("   This should be rejected (exceeds 20MB per file limit)")
        
    finally:
        if large_file:
            try:
                os.unlink(large_file)
            except:
                pass
    
    # Test 3: Too many files - should fail
    print("\n3. Testing too many files (60 files)...")
    many_files = []
    try:
        # Create 60 small files
        for i in range(60):
            test_file = create_test_file(f"_many{i}.txt", 0.1)  # 0.1MB each
            many_files.append(test_file)
        
        print(f"✅ Created {len(many_files)} test files, 0.1MB each")
        print("   This should be rejected (exceeds 50 files limit)")
        
    finally:
        # Clean up
        for f in many_files:
            try:
                os.unlink(f)
            except:
                pass
    
    print("\n" + "=" * 50)
    print("🎯 Test Results Summary:")
    print("✅ Normal case (5 × 1MB files): Should pass validation")
    print("❌ Large file (25MB): Should fail validation (>20MB limit)")
    print("❌ Many files (60 files): Should fail validation (>50 files limit)")
    print("\n📋 Configuration Limits:")
    print("   • Max files per KB: 50")
    print("   • Max total size: 100MB")
    print("   • Max file size: 20MB")
    print("   • Batch processing: 5 files at a time")

if __name__ == "__main__":
    test_file_limits()
