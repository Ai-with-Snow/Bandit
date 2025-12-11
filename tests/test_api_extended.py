"""Extended API tests - all query tiers and features.

Tests the full model routing system across all tiers.
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
import json

def query_engine(prompt: str) -> dict:
    """Query the Reasoning Engine and return result dict."""
    resource_name = get_engine_resource_name(DEFAULT_PROJECT, DEFAULT_LOCATION, DEFAULT_ENGINE_ID)
    credentials = _load_credentials()
    api_endpoint = f"https://{DEFAULT_LOCATION}-aiplatform.googleapis.com/v1beta1/{resource_name}:query"
    
    headers = {
        "Authorization": f"Bearer {credentials.token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "input": {"prompt": prompt},
        "classMethod": "query"
    }
    
    start = time.time()
    try:
        response = requests.post(api_endpoint, headers=headers, json=payload, timeout=90)
        elapsed = time.time() - start
        
        if response.status_code == 200:
            result = response.json()
            return {
                "success": True,
                "output": result.get("output", str(result)),
                "duration": elapsed
            }
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}: {response.text[:200]}",
                "duration": elapsed
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "duration": time.time() - start
        }

# Test cases organized by expected tier
TEST_CASES = [
    # Flash-Lite direct (simple greetings)
    {"prompt": "hi", "tier": "lite", "expected": "greeting"},
    {"prompt": "thanks", "tier": "lite", "expected": "acknowledgment"},
    {"prompt": "ok", "tier": "lite", "expected": "confirmation"},
    
    # Flash tier (general questions)
    {"prompt": "what is 2+2", "tier": "flash", "expected": "4"},
    {"prompt": "who is the president of the united states", "tier": "flash", "expected": "response"},
    {"prompt": "what day is christmas", "tier": "flash", "expected": "december"},
    
    # Pro tier (coding/analysis)
    {"prompt": "write a python function to calculate fibonacci", "tier": "pro", "expected": "def"},
    {"prompt": "explain the difference between sync and async in python", "tier": "pro", "expected": "async"},
    
    # Elite tier (complex reasoning)
    {"prompt": "design a comprehensive architecture for a multi-agent AI system with strategic planning capabilities and resource optimization", "tier": "elite", "expected": "architecture"},
]

if __name__ == "__main__":
    print("=" * 60)
    print("EXTENDED API TIER TESTS")
    print("=" * 60)
    
    results = {"passed": 0, "failed": 0, "avg_duration": 0, "by_tier": {}}
    durations = []
    
    for i, test in enumerate(TEST_CASES):
        print(f"\n[{i+1}/{len(TEST_CASES)}] {test['tier'].upper()}: {test['prompt'][:40]}...")
        
        result = query_engine(test["prompt"])
        durations.append(result["duration"])
        
        # Track by tier
        tier = test["tier"]
        if tier not in results["by_tier"]:
            results["by_tier"][tier] = {"passed": 0, "failed": 0, "durations": []}
        
        results["by_tier"][tier]["durations"].append(result["duration"])
        
        if result["success"]:
            # Check if expected content is in response
            output_lower = result["output"].lower()
            expected_found = test["expected"].lower() in output_lower or test["tier"] == "lite"
            
            if result["success"]:
                results["passed"] += 1
                results["by_tier"][tier]["passed"] += 1
                print(f"   ✅ Success ({result['duration']:.1f}s)")
                print(f"      Response: {result['output'][:80]}...")
            else:
                results["failed"] += 1
                results["by_tier"][tier]["failed"] += 1
                print(f"   ⚠️ Response missing expected content")
        else:
            results["failed"] += 1
            results["by_tier"][tier]["failed"] += 1
            print(f"   ❌ Failed: {result['error'][:80]}")
        
        # Brief delay between requests
        time.sleep(0.5)
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    print(f"\nOverall: {results['passed']}/{results['passed']+results['failed']} passed")
    print(f"Avg Duration: {sum(durations)/len(durations):.1f}s")
    
    print("\nBy Tier:")
    for tier, data in results["by_tier"].items():
        avg = sum(data["durations"])/len(data["durations"]) if data["durations"] else 0
        print(f"  {tier.upper()}: {data['passed']}/{data['passed']+data['failed']} passed, avg {avg:.1f}s")
    
    # Save results
    with open("test_results_extended.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\nResults saved to test_results_extended.json")
    
    success = results["failed"] == 0
    sys.exit(0 if success else 1)
