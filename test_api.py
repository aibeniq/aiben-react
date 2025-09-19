#!/usr/bin/env python3
"""
Simple test script to verify the Knowledge Base creation backend functionality
"""
import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
USERNAME = "admin@example.com"
PASSWORD = "cYJtxvYubNF40sx7sSlu1LFD9zhPaS7Ld75O"

def test_kb_creation():
    """Test knowledge base creation through the API"""
    
    # 1. Login
    print("1. Logging in...")
    login_data = {"username": USERNAME, "password": PASSWORD}
    response = requests.post(f"{BASE_URL}/login/access-token", data=login_data)
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code} - {response.text}")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login successful")
    
    # 2. Get embedding models
    print("2. Getting embedding models...")
    response = requests.get(f"{BASE_URL}/embedding-models/", headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Failed to get embedding models: {response.status_code} - {response.text}")
        return
    
    models = response.json()["data"]
    if not models:
        print("❌ No embedding models available")
        return
    
    embedding_model_id = models[0]["id"]
    print(f"✅ Using embedding model: {models[0]['name']} ({embedding_model_id})")
    
    # 3. Create knowledge base
    print("3. Creating knowledge base...")
    
    # Prepare multipart form data (files only)
    files = {
        'files': ('test_large.txt', open('test_large.txt', 'rb').read(), 'text/plain')
    }
    
    # Knowledge base data goes in query parameters
    params = {
        'title': f'Test Knowledge Base API {int(time.time())}',  # Add timestamp for uniqueness
        'description': 'A test knowledge base created via API with source entries',
        'embedding_model_id': embedding_model_id
    }
    
    response = requests.post(f"{BASE_URL}/knowledge-bases/", headers=headers, files=files, params=params)
    
    print(f"Response status: {response.status_code}")
    print(f"Response text: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        task_id = result.get("task_id")
        kb_id = result.get("knowledge_base", {}).get("id")
        
        print(f"✅ Knowledge base creation started!")
        print(f"   Task ID: {task_id}")
        print(f"   KB ID: {kb_id}")
        
        if task_id:
            # 4. Monitor progress
            print("4. Monitoring progress...")
            for i in range(60):  # Wait up to 60 seconds
                time.sleep(2)
                progress_response = requests.get(f"{BASE_URL}/knowledge-bases/progress/{task_id}", headers=headers)
                
                if progress_response.status_code == 200:
                    progress = progress_response.json()
                    status = progress.get("status", "unknown")
                    message = progress.get("message", "")
                    current = progress.get("current", 0)
                    total = progress.get("total", 0)
                    
                    print(f"   Progress: {current}/{total} - {status} - {message}")
                    
                    if status == "completed":
                        print("✅ Knowledge base created successfully!")
                        break
                    elif status == "failed":
                        print("❌ Knowledge base creation failed!")
                        print(f"   Error: {message}")
                        break
                else:
                    print(f"⚠️ Failed to get progress: {progress_response.status_code}")
                    if i % 5 == 0:  # Print every 10 seconds
                        print(f"   Continuing to wait... ({i*2}s elapsed)")
            else:
                print("⚠️ Timeout waiting for completion")
    else:
        print(f"❌ Failed to create knowledge base: {response.status_code}")
        try:
            error_detail = response.json()
            print(f"   Error details: {json.dumps(error_detail, indent=2)}")
        except:
            print(f"   Error text: {response.text}")

if __name__ == "__main__":
    print("🧪 Testing Knowledge Base Creation API")
    print("=" * 50)
    test_kb_creation()