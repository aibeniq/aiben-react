#!/usr/bin/env python3
"""
Quick test for Generate Report endpoint
"""
import requests
import json
import uuid

BASE_URL = "http://localhost:8000/api/v1"
USERNAME = "david@aiben.io"
PASSWORD = "password123456"
KB_ID = "7ec027b0-4ce6-4fbe-9ae4-d14ed69dc91e"

# Login
session = requests.Session()
login_data = {"username": USERNAME, "password": PASSWORD}
response = session.post(f"{BASE_URL}/login/access-token", data=login_data)
print(f"Login: {response.status_code}")

# Generate report with proper outline_id
sections_data = [
    {"text": "Product Overview", "consultDocuments": True},
    {"text": "Ingredients Analysis", "consultDocuments": True},
]

data = {
    "knowledge_base_id": KB_ID,
    "sections": json.dumps(sections_data),
    "outline_id": str(uuid.uuid4()),  # Use a real UUID
    "search_mode": "vector",
    "vision_analysis_override": "true",
    "pdf_parsing_override": "enhanced",
}

print(f"\nTesting Generate Report...")
print(f"Data: {data}")
response = session.post(f"{BASE_URL}/reportgenie/generate", data=data)
print(f"Status: {response.status_code}")
print(f"Response: {response.text[:500]}")
