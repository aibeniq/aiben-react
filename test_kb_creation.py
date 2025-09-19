#!/usr/bin/env python3
"""
Test script to verify Knowledge Base creation functionality
"""
import requests
import time
import json

# API base URL
BASE_URL = "http://localhost:8000/api/v1"

# Test credentials (you'll need to replace with actual test user)
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpassword"

def login():
    """Login and get auth token"""
    response = requests.post(
        f"{BASE_URL}/login/access-token",
        data={"username": TEST_EMAIL, "password": TEST_PASSWORD}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Login failed: {response.status_code} - {response.text}")
        return None

def test_kb_creation(token):
    """Test knowledge base creation"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # First, let's check available embedding models
    models_response = requests.get(f"{BASE_URL}/embedding-models/", headers=headers)
    if models_response.status_code == 200:
        models = models_response.json()
        if models:
            embedding_model_id = models[0]["id"]
            print(f"Using embedding model: {embedding_model_id}")
        else:
            print("No embedding models available")
            return
    else:
        print(f"Failed to get embedding models: {models_response.status_code}")
        return
    
    # Prepare form data for knowledge base creation
    files = {"files": ("test.txt", "This is a test document for knowledge base creation.", "text/plain")}
    data = {
        "title": "Test Knowledge Base",
        "description": "A test knowledge base",
        "embedding_model_id": embedding_model_id
    }
    
    # Create knowledge base
    print("Creating knowledge base...")
    response = requests.post(
        f"{BASE_URL}/knowledge-bases/",
        headers=headers,
        files=files,
        data=data
    )
    
    if response.status_code == 200:
        result = response.json()
        task_id = result.get("task_id")
        print(f"Knowledge base creation started! Task ID: {task_id}")
        
        if task_id:
            # Monitor progress
            for i in range(30):  # Wait up to 30 seconds
                progress_response = requests.get(f"{BASE_URL}/progress/{task_id}", headers=headers)
                if progress_response.status_code == 200:
                    progress = progress_response.json()
                    print(f"Progress: {progress}")
                    
                    if progress.get("status") == "completed":
                        print("✅ Knowledge base created successfully!")
                        break
                    elif progress.get("status") == "failed":
                        print("❌ Knowledge base creation failed!")
                        break
                else:
                    print(f"Failed to get progress: {progress_response.status_code}")
                
                time.sleep(1)
        
    else:
        print(f"Failed to create knowledge base: {response.status_code} - {response.text}")

if __name__ == "__main__":
    # Note: This test requires a valid user account
    print("Knowledge Base Creation Test")
    print("Note: This test requires valid credentials")
    print("You can test manually by visiting http://localhost:3000 and creating a knowledge base")