#!/usr/bin/env python3
"""
Test the new top-k highest risk endpoint
"""

import httpx

def test_endpoint():
    url = "http://localhost:8000/api/v1/query/top-k-highest-current-risk"
    payload = {"commodity": "Rice", "k": 5}
    
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.post(url, json=payload)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
            return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    test_endpoint()
