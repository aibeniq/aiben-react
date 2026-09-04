#!/usr/bin/env python3
"""
Test script to monitor progress in real-time
"""
import requests
import time
import json

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
USERNAME = "admin@example.com"
PASSWORD = "cYJtxvYubNF40sx7sSlu1LFD9zhPaS7Ld75O"

def test_progress_tracking():
    """Test progress tracking during knowledge base creation"""
    
    # Login
    login_data = {"username": USERNAME, "password": PASSWORD}
    response = requests.post(f"{BASE_URL}/login/access-token", data=login_data)
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get embedding models
    response = requests.get(f"{BASE_URL}/embedding-models/", headers=headers)
    models = response.json()["data"]
    embedding_model_id = models[0]["id"]
    
    # Create knowledge base with simple test file
    with open('test_simple.txt', 'rb') as f:
        files = {'files': ('test_simple.txt', f.read(), 'text/plain')}
    
    params = {
        'title': f'Progress Test KB {int(time.time())}',
        'description': 'Testing progress synchronization with simple file',
        'embedding_model_id': embedding_model_id
    }
    
    print("🚀 Starting knowledge base creation...")
    response = requests.post(f"{BASE_URL}/knowledge-bases/", headers=headers, files=files, params=params)
    
    result = response.json()
    task_id = result.get("task_id")
    print(f"📋 Task ID: {task_id}")
    
    # Monitor progress with detailed tracking
    progress_history = []
    for i in range(30):
        time.sleep(1)
        progress_response = requests.get(f"{BASE_URL}/knowledge-bases/progress/{task_id}", headers=headers)
        
        if progress_response.status_code == 200:
            progress = progress_response.json()
            status = progress.get("status", "unknown")
            message = progress.get("message", "")
            current = progress.get("current", 0)
            total = progress.get("total", 0)
            percentage = progress.get("percentage", 0)
            
            progress_entry = {
                "time": i,
                "status": status,
                "current": current,
                "total": total,
                "percentage": percentage,
                "message": message
            }
            progress_history.append(progress_entry)
            
            print(f"[{i:2d}s] {current}/{total} ({percentage:.1f}%) - {status} - {message}")
            
            if status in ["completed", "failed"]:
                break
    
    print("\n📊 Progress Summary:")
    print("Time | Current/Total | % | Status | Message")
    print("-" * 80)
    for entry in progress_history:
        print(f"{entry['time']:3d}s | {entry['current']:4.1f}/{entry['total']:4.1f} | {entry['percentage']:5.1f}% | {entry['status']:<9} | {entry['message'][:40]}")

if __name__ == "__main__":
    test_progress_tracking()