#!/usr/bin/env python3
"""
Test script to verify debug prints are working
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import app
from fastapi.testclient import TestClient

print("Testing the application with debug prints...")

# Create test client
client = TestClient(app)

print("Making request to /api/v1/health...")
response = client.get("/api/v1/health")
print(f"Health response: {response.json()}")

print("\nMaking request to /api/v1/todos with fake token...")
response = client.get("/api/v1/todos", headers={
    "Authorization": "Bearer fake-token"
})
print(f"Todos response: {response.json()}")
print(f"Status code: {response.status_code}")