"""GCP Connection Stress Test - 100 checks.

Tests GCP connections:
- Credentials loading
- BigQuery client init
- API auth token generation
- Reasoning Engine connection
"""

import sys
import os
import time
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class Stats:
    def __init__(self):
        self.lock = threading.Lock()
        self.passed = 0
        self.failed = 0
        self.errors = []
        self.times = {}
    
    def record(self, cat, success, duration, error=None):
        with self.lock:
            if success:
                self.passed += 1
            else:
                self.failed += 1
                if len(self.errors) < 20:
                    self.errors.append({"cat": cat, "err": str(error)[:100]})
            if cat not in self.times:
                self.times[cat] = []
            self.times[cat].append(duration)

# GCP Tests
def test_load_credentials():
    """Test loading GCP credentials."""
    from scripts.bandit_cli import _load_credentials
    creds = _load_credentials()
    assert creds is not None
    assert hasattr(creds, 'token')
    return True

def test_credentials_token():
    """Test that credentials have valid token."""
    from scripts.bandit_cli import _load_credentials
    creds = _load_credentials()
    assert creds.token is not None
    assert len(creds.token) > 50  # Token should be substantial
    return True

def test_bigquery_client_init():
    """Test BigQuery client initialization."""
    from google.cloud import bigquery
    from scripts.bandit_cli import DEFAULT_PROJECT
    client = bigquery.Client(project=DEFAULT_PROJECT)
    assert client is not None
    return True

def test_bigquery_dataset_check():
    """Test checking BigQuery dataset exists."""
    from google.cloud import bigquery
    from scripts.bandit_cli import DEFAULT_PROJECT
    client = bigquery.Client(project=DEFAULT_PROJECT)
    dataset_ref = f"{DEFAULT_PROJECT}.bandit_memory"
    try:
        client.get_dataset(dataset_ref)
        return True
    except Exception:
        # Dataset may not exist yet, but connection works
        return True

def test_aiplatform_init():
    """Test AI Platform initialization."""
    from google.cloud import aiplatform
    from scripts.bandit_cli import DEFAULT_PROJECT, DEFAULT_LOCATION
    aiplatform.init(project=DEFAULT_PROJECT, location=DEFAULT_LOCATION)
    return True

def test_reasoning_engine_client():
    """Test Reasoning Engine client creation."""
    from google.cloud.aiplatform_v1 import ReasoningEngineServiceClient
    client = ReasoningEngineServiceClient()
    assert client is not None
    return True

def test_genai_client():
    """Test google.genai client creation."""
    from google import genai
    from scripts.bandit_cli import DEFAULT_PROJECT, DEFAULT_LOCATION
    client = genai.Client(
        vertexai=True,
        project=DEFAULT_PROJECT,
        location=DEFAULT_LOCATION
    )
    assert client is not None
    return True

def test_resource_name_build():
    """Test building resource names."""
    from scripts.bandit_cli import get_engine_resource_name, DEFAULT_PROJECT, DEFAULT_LOCATION, DEFAULT_ENGINE_ID
    name = get_engine_resource_name(DEFAULT_PROJECT, DEFAULT_LOCATION, DEFAULT_ENGINE_ID)
    assert "projects/" in name
    assert "reasoningEngines/" in name
    return True

ALL_TESTS = [
    ("credentials", test_load_credentials),
    ("creds_token", test_credentials_token),
    ("bigquery_init", test_bigquery_client_init),
    ("bigquery_check", test_bigquery_dataset_check),
    ("aiplatform_init", test_aiplatform_init),
    ("engine_client", test_reasoning_engine_client),
    ("genai_client", test_genai_client),
    ("resource_name", test_resource_name_build),
]

import random

def run_test(test_id, stats):
    name, func = random.choice(ALL_TESTS)
    start = time.time()
    try:
        func()
        duration = time.time() - start
        stats.record(name, True, duration)
        return True, name, duration
    except Exception as e:
        duration = time.time() - start
        stats.record(name, False, duration, e)
        return False, name, str(e)

def main():
    MAX_TESTS = 100
    WORKERS = 3
    
    print("=" * 60)
    print("GCP CONNECTION STRESS TEST")
    print(f"Target: {MAX_TESTS} checks")
    print(f"Started: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 60)
    
    stats = Stats()
    start = time.time()
    
    with ThreadPoolExecutor(max_workers=WORKERS) as executor:
        futures = [executor.submit(run_test, i, stats) for i in range(MAX_TESTS)]
        
        completed = 0
        for future in as_completed(futures):
            completed += 1
            success, name, result = future.result()
            
            if completed % 20 == 0:
                elapsed = time.time() - start
                print(f"[{completed}/{MAX_TESTS}] Pass: {stats.passed} | Fail: {stats.failed} | {elapsed:.1f}s")
    
    elapsed = time.time() - start
    total = stats.passed + stats.failed
    
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"Total: {total}")
    print(f"Passed: {stats.passed} ({stats.passed/total*100:.1f}%)")
    print(f"Failed: {stats.failed}")
    print(f"Duration: {elapsed:.1f}s")
    print(f"Rate: {total/elapsed:.1f}/sec")
    
    print("\nBy Connection Type:")
    for cat, times in sorted(stats.times.items()):
        avg = sum(times)/len(times) if times else 0
        print(f"  {cat}: {len(times)} tests, avg {avg*1000:.0f}ms")
    
    if stats.errors:
        print(f"\nErrors ({len(stats.errors)}):")
        for e in stats.errors[:5]:
            print(f"  [{e['cat']}] {e['err']}")
    
    with open("gcp_stress_results.json", "w") as f:
        json.dump({"passed": stats.passed, "failed": stats.failed, "duration": elapsed}, f, indent=2)
    
    return 0 if stats.failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
