"""Comprehensive Bandit Test Suite - 300 Checks

Tests all Bandit features except image/video generation.
Run for 15 minutes with various query types.
"""

import subprocess
import time
import json
import sys
from datetime import datetime
from pathlib import Path

# Test categories
GREETING_TESTS = [
    "hi", "hey", "hello", "yo", "sup", "good morning", "thanks", "ok"
]

SIMPLE_QUERIES = [
    "what time is it",
    "what day is it today",
    "who are you",
    "what can you do",
    "tell me a joke",
    "how are you",
]

MODERATE_QUERIES = [
    "explain what a reasoning engine is",
    "what is the difference between flash and pro models",
    "describe the bandit project",
    "what is vertex ai",
    "explain google cloud platform",
    "what is gemini",
]

CODING_QUERIES = [
    "write a python function to reverse a string",
    "explain how async await works in python",
    "what is a decorator in python",
    "show me a simple flask hello world",
    "explain list comprehensions",
]

COMPLEX_QUERIES = [
    "analyze the trade-offs between using flash-lite vs pro for routing queries",
    "design a multi-agent system architecture for task orchestration",
    "explain the strategic planning process for scaling a startup",
    "synthesize information about memory management patterns in distributed systems",
]

COMMAND_TESTS = [
    "/help",
    "/search what is vertex ai",
]

def run_bandit_query(prompt: str, timeout: int = 60) -> dict:
    """Run a single query through Bandit CLI and capture result."""
    start = time.time()
    result = {
        "prompt": prompt,
        "success": False,
        "response": "",
        "error": "",
        "duration": 0
    }
    
    try:
        # Use echo to send input to bandit, then exit
        process = subprocess.run(
            ["powershell", "-Command", f'echo "{prompt}`nexit" | .venv\\Scripts\\python.exe scripts/bandit_cli.py'],
            cwd=r"c:\Users\Goddexx Snow\Documents\bandit",
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        result["response"] = process.stdout[-2000:] if len(process.stdout) > 2000 else process.stdout
        result["error"] = process.stderr[-500:] if len(process.stderr) > 500 else process.stderr
        result["success"] = process.returncode == 0 and "Error" not in process.stderr
        
    except subprocess.TimeoutExpired:
        result["error"] = "TIMEOUT"
    except Exception as e:
        result["error"] = str(e)
    
    result["duration"] = time.time() - start
    return result

def main():
    print("=" * 60)
    print("BANDIT COMPREHENSIVE TEST SUITE")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Build test queue - cycle through categories
    all_tests = []
    
    # Add tests in rounds to get variety
    for i in range(10):
        all_tests.extend(GREETING_TESTS)
        all_tests.extend(SIMPLE_QUERIES)
        all_tests.extend(MODERATE_QUERIES)
        all_tests.extend(CODING_QUERIES)
        all_tests.extend(COMPLEX_QUERIES)
        all_tests.extend(COMMAND_TESTS)
    
    # Limit to 300 tests
    all_tests = all_tests[:300]
    
    results = {
        "total": len(all_tests),
        "passed": 0,
        "failed": 0,
        "timeouts": 0,
        "errors": [],
        "durations": []
    }
    
    start_time = time.time()
    max_duration = 15 * 60  # 15 minutes
    
    for i, test in enumerate(all_tests):
        # Check time limit
        elapsed = time.time() - start_time
        if elapsed > max_duration:
            print(f"\n⏰ Time limit reached ({max_duration/60:.0f} min)")
            break
        
        print(f"\n[{i+1}/{len(all_tests)}] Testing: {test[:50]}...")
        
        result = run_bandit_query(test)
        results["durations"].append(result["duration"])
        
        if result["success"]:
            results["passed"] += 1
            print(f"  ✅ PASS ({result['duration']:.1f}s)")
        elif result["error"] == "TIMEOUT":
            results["timeouts"] += 1
            results["failed"] += 1
            print(f"  ⏰ TIMEOUT")
            results["errors"].append({"test": test, "error": "TIMEOUT"})
        else:
            results["failed"] += 1
            print(f"  ❌ FAIL: {result['error'][:100]}")
            results["errors"].append({"test": test, "error": result["error"][:200]})
        
        # Small delay between tests
        time.sleep(0.5)
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests Run: {results['passed'] + results['failed']}")
    print(f"Passed: {results['passed']}")
    print(f"Failed: {results['failed']}")
    print(f"Timeouts: {results['timeouts']}")
    
    if results["durations"]:
        avg_duration = sum(results["durations"]) / len(results["durations"])
        print(f"Avg Duration: {avg_duration:.1f}s")
    
    if results["errors"]:
        print(f"\nErrors ({len(results['errors'])}):")
        for err in results["errors"][:10]:
            print(f"  - {err['test'][:30]}: {err['error'][:50]}")
    
    # Save results
    results_file = Path("test_results.json")
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {results_file}")
    
    return 0 if results["failed"] == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
