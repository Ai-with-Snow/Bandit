"""API Integration tests for Bandit Reasoning Engine.

Tests actual API calls to the deployed Reasoning Engine.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.bandit_cli import (
    get_engine_resource_name,
    _load_credentials,
    DEFAULT_PROJECT,
    DEFAULT_LOCATION,
    DEFAULT_ENGINE_ID,
)
import requests
import time

def test_reasoning_engine_query():
    """Test a simple query to the Reasoning Engine."""
    print("\n🔌 Testing Reasoning Engine API...")
    
    # Build resource name
    resource_name = get_engine_resource_name(DEFAULT_PROJECT, DEFAULT_LOCATION, DEFAULT_ENGINE_ID)
    print(f"   Resource: {resource_name}")
    
    # Get credentials
    credentials = _load_credentials()
    
    # Build request
    api_endpoint = f"https://{DEFAULT_LOCATION}-aiplatform.googleapis.com/v1beta1/{resource_name}:query"
    
    headers = {
        "Authorization": f"Bearer {credentials.token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "input": {"prompt": "Say 'API test successful' and nothing else."},
        "classMethod": "query"
    }
    
    print(f"   Endpoint: {api_endpoint[:80]}...")
    print("   Sending request...")
    
    start = time.time()
    try:
        response = requests.post(api_endpoint, headers=headers, json=payload, timeout=60)
        elapsed = time.time() - start
        
        if response.status_code == 200:
            result = response.json()
            output = result.get("output", str(result))
            print(f"   ✅ API Response ({elapsed:.1f}s):")
            print(f"      {output[:200]}")
            return True
        else:
            print(f"   ❌ API Error {response.status_code}:")
            print(f"      {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print("   ⏰ Request timed out (60s)")
        return False
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False

def test_simple_greeting():
    """Test simple greeting (should use Flash-Lite via routing)."""
    print("\n👋 Testing simple greeting (Flash-Lite routing)...")
    
    resource_name = get_engine_resource_name(DEFAULT_PROJECT, DEFAULT_LOCATION, DEFAULT_ENGINE_ID)
    credentials = _load_credentials()
    api_endpoint = f"https://{DEFAULT_LOCATION}-aiplatform.googleapis.com/v1beta1/{resource_name}:query"
    
    headers = {
        "Authorization": f"Bearer {credentials.token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "input": {"prompt": "hi"},
        "classMethod": "query"
    }
    
    start = time.time()
    try:
        response = requests.post(api_endpoint, headers=headers, json=payload, timeout=60)
        elapsed = time.time() - start
        
        if response.status_code == 200:
            result = response.json()
            output = result.get("output", str(result))
            print(f"   ✅ Greeting response ({elapsed:.1f}s):")
            print(f"      {output[:200]}")
            return True
        else:
            print(f"   ❌ Error {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("BANDIT API INTEGRATION TESTS")
    print("=" * 50)
    
    results = []
    
    results.append(("Reasoning Engine Query", test_reasoning_engine_query()))
    results.append(("Simple Greeting", test_simple_greeting()))
    
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"  {status} {name}")
    
    print(f"\nPassed: {passed}/{total}")
    
    sys.exit(0 if passed == total else 1)
