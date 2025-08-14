#!/usr/bin/env python3
"""
Test script to verify Redis connection and session management functionality.
"""
import sys
import os
import uuid

# Add the backend app to the path
sys.path.append('/app')

from app.services.session_manager import session_manager

def test_redis_connection():
    """Test basic Redis connection and session operations"""
    print("Testing Redis connection and session management...")
    
    # Test session operations
    test_session_id = str(uuid.uuid4())
    test_data = {
        "user_id": "test_user",
        "timestamp": "2024-01-01T00:00:00",
        "data": {"key": "value"}
    }
    
    print(f"Testing with session ID: {test_session_id}")
    
    # Test setting session data
    print("Setting session data...")
    success = session_manager.set_session(test_session_id, test_data)
    print(f"Set session result: {success}")
    
    # Test getting session data
    print("Getting session data...")
    retrieved_data = session_manager.get_session(test_session_id)
    print(f"Retrieved session data: {retrieved_data}")
    
    # Test session deletion
    print("Deleting session...")
    delete_success = session_manager.delete_session(test_session_id)
    print(f"Delete session result: {delete_success}")
    
    # Verify deletion
    print("Verifying deletion...")
    deleted_data = session_manager.get_session(test_session_id)
    print(f"Data after deletion: {deleted_data}")
    
    print("Redis connection test completed!")

if __name__ == "__main__":
    test_redis_connection()
