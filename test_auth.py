#\!/usr/bin/env python3
"""
Quick test to verify auth implementation works correctly.
Tests both header-based and payload-based auth.
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_ENDPOINT = os.getenv("API_ENDPOINT", "http://127.0.0.1:8000/generate_answers/")
API_AUTH_TOKEN = os.getenv("API_AUTH_TOKEN")

def test_header_auth():
    """Test X-API-Key header auth (preferred method)"""
    print("Testing X-API-Key header auth...")
    payload = {
        "user_question": "Test question",
        "user_model": "gpt-4o"
    }
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': API_AUTH_TOKEN
    }
    try:
        response = requests.post(API_ENDPOINT, headers=headers, json=payload, timeout=5)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            print("  ✅ Header auth works\!")
        else:
            print(f"  ❌ Failed: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_payload_auth():
    """Test payload user_auth (backward compatible)"""
    print("\nTesting payload user_auth (backward compatible)...")
    payload = {
        "user_question": "Test question",
        "user_model": "gpt-4o",
        "user_auth": API_AUTH_TOKEN
    }
    headers = {
        'Content-Type': 'application/json'
    }
    try:
        response = requests.post(API_ENDPOINT, headers=headers, json=payload, timeout=5)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            print("  ✅ Payload auth works\!")
        else:
            print(f"  ❌ Failed: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_both_auth():
    """Test with both header and payload (header should take precedence)"""
    print("\nTesting both header and payload (header should win)...")
    payload = {
        "user_question": "Test question",
        "user_model": "gpt-4o",
        "user_auth": API_AUTH_TOKEN
    }
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': API_AUTH_TOKEN
    }
    try:
        response = requests.post(API_ENDPOINT, headers=headers, json=payload, timeout=5)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            print("  ✅ Both auth methods work together\!")
        else:
            print(f"  ❌ Failed: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_no_auth():
    """Test without any auth (should fail)"""
    print("\nTesting without auth (should fail with 401)...")
    payload = {
        "user_question": "Test question",
        "user_model": "gpt-4o"
    }
    headers = {
        'Content-Type': 'application/json'
    }
    try:
        response = requests.post(API_ENDPOINT, headers=headers, json=payload, timeout=5)
        print(f"  Status: {response.status_code}")
        if response.status_code == 401:
            print("  ✅ Correctly rejected unauthorized request\!")
            return True
        else:
            print(f"  ❌ Should have returned 401, got {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("API Authentication Test Suite")
    print("=" * 60)
    print(f"Endpoint: {API_ENDPOINT}")
    print(f"Token configured: {'Yes' if API_AUTH_TOKEN else 'No'}")
    print("=" * 60)
    
    if not API_AUTH_TOKEN:
        print("❌ API_AUTH_TOKEN not set in .env")
        exit(1)
    
    results = []
    results.append(("Header auth", test_header_auth()))
    results.append(("Payload auth", test_payload_auth()))
    results.append(("Both auth", test_both_auth()))
    results.append(("No auth (should fail)", test_no_auth()))
    
    print("\n" + "=" * 60)
    print("Test Results:")
    print("=" * 60)
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(result[1] for result in results)
    print("=" * 60)
    if all_passed:
        print("✅ All tests passed\!")
        exit(0)
    else:
        print("❌ Some tests failed")
        exit(1)
