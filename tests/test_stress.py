"""Deep Stress Test - 500 checks over 30 minutes.

Tests Bandit Reasoning Engine under sustained load.
No image/video generation.
"""

import sys
import os
import time
import json
import random
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.bandit_cli import (
    get_engine_resource_name,
    _load_credentials,
    DEFAULT_PROJECT,
    DEFAULT_LOCATION,
    DEFAULT_ENGINE_ID,
)
import requests

# Query pools by tier
LITE_QUERIES = [
    "hi", "hey", "hello", "yo", "sup", "thanks", "ok", "yes", "no", "cool",
    "good morning", "good afternoon", "good evening", "yep", "sure", "nice"
]

FLASH_QUERIES = [
    "what is 2+2",
    "what day is today",
    "who are you",
    "tell me a joke",
    "what is python",
    "what is javascript",
    "what time is it",
    "what year is it",
    "count to 5",
    "what color is the sky",
    "spell the word hello",
    "what is 10 divided by 2",
]

PRO_QUERIES = [
    "write a python function to check if a number is prime",
    "explain recursion in programming",
    "what is the difference between a list and a tuple in python",
    "write a simple REST API endpoint",
    "explain object-oriented programming",
    "write a binary search function",
    "explain how garbage collection works",
    "what is dependency injection",
]

ELITE_QUERIES = [
    "design a comprehensive microservices architecture for an e-commerce platform",
    "analyze the trade-offs between SQL and NoSQL databases for a social media application",
    "create a strategic plan for migrating a monolithic application to cloud-native architecture",
    "synthesize best practices for building fault-tolerant distributed systems",
]

# Weights for tier selection (favor faster tiers for stress test)
TIER_WEIGHTS = {
    "lite": 50,    # 50% lite - fast
    "flash": 30,   # 30% flash
    "pro": 15,     # 15% pro
    "elite": 5,    # 5% elite - slow
}

def get_random_query():
    """Get a random query weighted by tier."""
    roll = random.randint(1, 100)
    
    if roll <= TIER_WEIGHTS["lite"]:
        return random.choice(LITE_QUERIES), "lite"
    elif roll <= TIER_WEIGHTS["lite"] + TIER_WEIGHTS["flash"]:
        return random.choice(FLASH_QUERIES), "flash"
    elif roll <= TIER_WEIGHTS["lite"] + TIER_WEIGHTS["flash"] + TIER_WEIGHTS["pro"]:
        return random.choice(PRO_QUERIES), "pro"
    else:
        return random.choice(ELITE_QUERIES), "elite"

# Thread-safe counters
class StressStats:
    def __init__(self):
        self.lock = threading.Lock()
        self.passed = 0
        self.failed = 0
        self.timeouts = 0
        self.errors = []
        self.tier_stats = {"lite": [], "flash": [], "pro": [], "elite": []}
    
    def record_success(self, tier, duration):
        with self.lock:
            self.passed += 1
            self.tier_stats[tier].append(duration)
    
    def record_failure(self, tier, error):
        with self.lock:
            self.failed += 1
            if len(self.errors) < 50:  # Cap error list
                self.errors.append({"tier": tier, "error": str(error)[:100]})
    
    def record_timeout(self, tier):
        with self.lock:
            self.timeouts += 1
            self.failed += 1

def query_engine(prompt: str, timeout: int = 90):
    """Query the Reasoning Engine."""
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
    response = requests.post(api_endpoint, headers=headers, json=payload, timeout=timeout)
    elapsed = time.time() - start
    
    if response.status_code == 200:
        return True, elapsed, None
    else:
        return False, elapsed, f"HTTP {response.status_code}"

def run_single_test(test_id: int, stats: StressStats):
    """Run a single test."""
    prompt, tier = get_random_query()
    
    try:
        success, duration, error = query_engine(prompt)
        
        if success:
            stats.record_success(tier, duration)
            return True, tier, duration
        else:
            stats.record_failure(tier, error)
            return False, tier, error
            
    except requests.exceptions.Timeout:
        stats.record_timeout(tier)
        return False, tier, "TIMEOUT"
    except Exception as e:
        stats.record_failure(tier, str(e))
        return False, tier, str(e)

def main():
    MAX_TESTS = 500
    MAX_DURATION = 30 * 60  # 30 minutes
    CONCURRENT_WORKERS = 3  # Parallel requests
    
    print("=" * 70)
    print("BANDIT DEEP STRESS TEST")
    print(f"Target: {MAX_TESTS} checks over {MAX_DURATION//60} minutes")
    print(f"Concurrent workers: {CONCURRENT_WORKERS}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    stats = StressStats()
    start_time = time.time()
    completed = 0
    
    with ThreadPoolExecutor(max_workers=CONCURRENT_WORKERS) as executor:
        # Submit all tasks
        futures = []
        for i in range(MAX_TESTS):
            futures.append(executor.submit(run_single_test, i, stats))
        
        # Process as they complete
        for future in as_completed(futures):
            completed += 1
            elapsed = time.time() - start_time
            
            # Check time limit
            if elapsed > MAX_DURATION:
                print(f"\n⏰ Time limit reached ({MAX_DURATION//60} min)")
                executor.shutdown(wait=False)
                break
            
            try:
                success, tier, result = future.result()
                status = "✅" if success else "❌"
                detail = f"{result:.1f}s" if success else result[:20]
                
                # Progress every 10 tests
                if completed % 10 == 0:
                    rate = completed / elapsed * 60 if elapsed > 0 else 0
                    print(f"[{completed}/{MAX_TESTS}] {status} {tier.upper()} | "
                          f"Pass: {stats.passed} | Fail: {stats.failed} | "
                          f"Elapsed: {elapsed/60:.1f}min | Rate: {rate:.1f}/min")
                    
            except Exception as e:
                print(f"[{completed}] ❌ Exception: {e}")
    
    # Final stats
    elapsed = time.time() - start_time
    total_tests = stats.passed + stats.failed
    
    print("\n" + "=" * 70)
    print("FINAL RESULTS")
    print("=" * 70)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {stats.passed} ({stats.passed/total_tests*100:.1f}%)")
    print(f"Failed: {stats.failed}")
    print(f"Timeouts: {stats.timeouts}")
    print(f"Duration: {elapsed/60:.1f} minutes")
    print(f"Rate: {total_tests/elapsed*60:.1f} tests/minute")
    
    print("\nBy Tier:")
    for tier, durations in stats.tier_stats.items():
        if durations:
            avg = sum(durations) / len(durations)
            print(f"  {tier.upper()}: {len(durations)} tests, avg {avg:.1f}s")
    
    if stats.errors:
        print(f"\nSample Errors ({len(stats.errors)}):")
        for err in stats.errors[:5]:
            print(f"  - [{err['tier']}] {err['error']}")
    
    # Save results
    results = {
        "total": total_tests,
        "passed": stats.passed,
        "failed": stats.failed,
        "timeouts": stats.timeouts,
        "duration_seconds": elapsed,
        "tier_counts": {t: len(d) for t, d in stats.tier_stats.items()},
        "tier_avgs": {t: sum(d)/len(d) if d else 0 for t, d in stats.tier_stats.items()},
        "errors": stats.errors[:20],
    }
    
    with open("stress_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nResults saved to stress_test_results.json")
    
    success_rate = stats.passed / total_tests if total_tests > 0 else 0
    return 0 if success_rate >= 0.95 else 1

if __name__ == "__main__":
    sys.exit(main())
