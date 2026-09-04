#!/usr/bin/env python3
"""
Test script to verify that our cancellation mechanism works.
This will create a simple HTTP request to the compare endpoint and then cancel it.
"""

import requests
import time
import threading
import sys

def make_request():
    """Make a request to the compare endpoint"""
    url = "http://localhost:8000/api/v1/twincheck/compare"
    
    # Create some simple test files
    files = {
        'document1': ('test1.txt', 'This is a test document with some content.\nLine 2 of the document.\nLine 3 with more text.', 'text/plain'),
        'document2': ('test2.txt', 'This is a test document with different content.\nLine 2 is changed.\nLine 3 has new text.', 'text/plain')
    }
    
    data = {
        'comparison_topics': 'Content differences\nStructural changes\nWord choice variations'
    }
    
    print("Starting comparison request...")
    start_time = time.time()
    
    try:
        # Make the request with a short timeout to see if it gets cancelled
        response = requests.post(url, files=files, data=data, timeout=10)
        print(f"Request completed in {time.time() - start_time:.2f}s")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
    except requests.exceptions.Timeout:
        print(f"Request timed out after {time.time() - start_time:.2f}s")
    except requests.exceptions.ConnectionError as e:
        print(f"Connection error after {time.time() - start_time:.2f}s: {e}")
    except Exception as e:
        print(f"Error after {time.time() - start_time:.2f}s: {e}")

def cancel_request_test():
    """Test cancelling a request mid-flight"""
    url = "http://localhost:8000/api/v1/twincheck/compare"
    
    files = {
        'document1': ('test1.txt', 'This is a test document with some content.\nLine 2 of the document.\nLine 3 with more text.', 'text/plain'),
        'document2': ('test2.txt', 'This is a test document with different content.\nLine 2 is changed.\nLine 3 has new text.', 'text/plain')
    }
    
    data = {
        'comparison_topics': 'Content differences\nStructural changes\nWord choice variations\nTone analysis\nReadability assessment'
    }
    
    print("Starting request that will be cancelled...")
    start_time = time.time()
    
    # Create a session that we can control
    session = requests.Session()
    
    def make_request():
        try:
            response = session.post(url, files=files, data=data, timeout=30)
            print(f"Request completed unexpectedly in {time.time() - start_time:.2f}s")
            print(f"Status: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Request cancelled/failed after {time.time() - start_time:.2f}s: {e}")
    
    # Start the request in a thread
    request_thread = threading.Thread(target=make_request)
    request_thread.start()
    
    # Wait 3 seconds then close the session to simulate client disconnection
    time.sleep(3)
    print(f"Closing session after {time.time() - start_time:.2f}s...")
    session.close()
    
    # Wait for the thread to finish
    request_thread.join(timeout=10)
    
    print(f"Test completed after {time.time() - start_time:.2f}s")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "cancel":
        cancel_request_test()
    else:
        make_request()