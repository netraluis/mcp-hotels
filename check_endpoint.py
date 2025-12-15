#!/usr/bin/env python3
"""
Script to verify that the SSE endpoint is responding.
"""
import requests
import sys
import os

url = os.environ.get("MCP_URL", "http://localhost:8000")
sse_url = f"{url}/sse"

print(f"Checking endpoint: {sse_url}")

try:
    response = requests.get(sse_url, timeout=5)
    print(f"Status: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    print(f"Content-Type: {response.headers.get('Content-Type', 'N/A')}")
    
    if response.status_code == 200:
        print("OK: Endpoint responding correctly")
    else:
        print(f"ERROR: Endpoint responded with status {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
except requests.exceptions.ConnectionError:
    print("ERROR: Cannot connect to server")
    print("   Make sure the server is running")
except Exception as e:
    print(f"ERROR: {e}")
