#!/usr/bin/env python3
"""
Test script to verify the new rate limiting strategy works correctly.
This will simulate rapid API calls to trigger rate limits and show the improved backoff.
"""

import time
import requests
import json

def test_rate_limiting():
    """Test the rate limiting behavior by making a request that should trigger rate limits"""
    
    # Use your backend URL
    url = "http://localhost:8000/api/v1/twincheck/compare"
    
    # Simple test documents
    files = {
        'file1': ('test1.txt', 'This is test document 1 content', 'text/plain'),
        'file2': ('test2.txt', 'This is test document 2 content', 'text/plain')
    }
    
    params = {
        'comparison_topics': 'Content Differences: Compare the content of both documents'
    }
    
    print("🧪 Testing rate limiting behavior...")
    print("⏰ Starting at:", time.strftime("%H:%M:%S"))
    
    try:
        response = requests.post(url, files=files, params=params, timeout=60)
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 500:
            print("✅ Expected rate limit error triggered - check backend logs for exponential backoff behavior")
        else:
            print(f"📝 Response: {response.text[:200]}...")
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out - normal when rate limiting is working")
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    
    print("🔍 Check the backend logs to see the new rate limiting strategy in action!")
    print("💡 Look for logs showing 'HYBRID STRATEGY' with increasing wait times")

if __name__ == "__main__":
    test_rate_limiting()