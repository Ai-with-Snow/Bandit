"""CLI Component Stress Test - 500 checks over 30 minutes.

Tests CLI components WITHOUT hitting the model API:
- MemoryManager operations
- File I/O (local JSON, SQLite paths)
- Import stability
- Resource handling
- Context generation
"""

import sys
import os
import time
import json
import random
import threading
import gc
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Thread-safe stats
class Stats:
    def __init__(self):
        self.lock = threading.Lock()
        self.passed = 0
        self.failed = 0
        self.errors = []
        self.category_times = {}
    
    def record(self, category, success, duration, error=None):
        with self.lock:
            if success:
                self.passed += 1
            else:
                self.failed += 1
                if len(self.errors) < 50:
                    self.errors.append({"cat": category, "err": str(error)[:100]})
            
            if category not in self.category_times:
                self.category_times[category] = []
            self.category_times[category].append(duration)

# Test functions
def test_memory_manager_create():
    """Test creating MemoryManager instances."""
    from scripts.bandit_cli import MemoryManager
    m = MemoryManager("test-project")
    assert m.project_id == "test-project"
    assert m.conversation_history == []
    return True

def test_memory_add_messages():
    """Test adding many messages."""
    from scripts.bandit_cli import MemoryManager
    m = MemoryManager("test-project")
    for i in range(100):
        m.add_message("user", f"Message {i}")
        m.add_message("bandit", f"Response {i}")
    assert len(m.conversation_history) == 200
    return True

def test_memory_limit():
    """Test memory limit enforcement."""
    from scripts.bandit_cli import MemoryManager, SHORT_TERM_MEMORY_LIMIT
    m = MemoryManager("test-project")
    for i in range(SHORT_TERM_MEMORY_LIMIT + 200):
        m.add_message("user", f"Msg {i}")
    assert len(m.conversation_history) == SHORT_TERM_MEMORY_LIMIT
    return True

def test_context_generation():
    """Test context generation with many messages."""
    from scripts.bandit_cli import MemoryManager
    m = MemoryManager("test-project")
    for i in range(50):
        m.add_message("user", f"Question {i}")
        m.add_message("bandit", f"Answer {i}")
    ctx = m.get_context()
    assert len(ctx) > 100
    assert "USER:" in ctx
    return True

def test_primer_context():
    """Test primer context integration."""
    from scripts.bandit_cli import MemoryManager
    m = MemoryManager("test-project")
    m.primer_context = "Test primer content"
    m.add_message("user", "hello")
    ctx = m.get_context()
    assert "[PRIMER]" in ctx
    return True

def test_timezone():
    """Test timezone is correct."""
    from scripts.bandit_cli import TIMEZONE
    assert str(TIMEZONE) == "America/New_York"
    return True

def test_imports_bandit_cli():
    """Test all bandit_cli imports work."""
    from scripts.bandit_cli import (
        MemoryManager, 
        get_engine_resource_name,
        DEFAULT_PROJECT,
        DEFAULT_LOCATION,
        DEFAULT_ENGINE_ID,
        SHORT_TERM_MEMORY_LIMIT,
        TIMEZONE,
    )
    return True

def test_imports_council():
    """Test council imports work."""
    from scripts.council import (
        BANDIT_PROFILE,
        ICEWIRE_PROFILE,
        CIPHER_PROFILE,
        run_council,
    )
    return True

def test_imports_prompting():
    """Test prompting imports work."""
    from scripts.prompting import (
        tree_of_thought,
        battle_of_bots,
        optimize_prompt,
    )
    return True

def test_imports_deploy():
    """Test deploy imports work."""
    from scripts.deploy_reasoning_engine import (
        MODEL_COSTS,
        SEARCH_KEYWORDS,
        BanditEngine,
    )
    return True

def test_resource_name():
    """Test resource name generation."""
    from scripts.bandit_cli import get_engine_resource_name
    result = get_engine_resource_name("proj", "loc", "engine123")
    assert result == "projects/proj/locations/loc/reasoningEngines/engine123"
    return True

def test_json_serialization():
    """Test JSON serialization of conversation history."""
    from scripts.bandit_cli import MemoryManager
    m = MemoryManager("test-project")
    m.add_message("user", "hello")
    m.add_message("bandit", "hi there")
    data = json.dumps({"history": m.conversation_history})
    loaded = json.loads(data)
    assert len(loaded["history"]) == 2
    return True

def test_memory_gc():
    """Test memory cleanup after manager deletion."""
    from scripts.bandit_cli import MemoryManager
    for _ in range(10):
        m = MemoryManager("test-project")
        for i in range(500):
            m.add_message("user", f"test message {i}" * 10)
        del m
    gc.collect()
    return True

# All tests
ALL_TESTS = [
    ("memory_create", test_memory_manager_create),
    ("memory_add", test_memory_add_messages),
    ("memory_limit", test_memory_limit),
    ("context_gen", test_context_generation),
    ("primer", test_primer_context),
    ("timezone", test_timezone),
    ("imports_cli", test_imports_bandit_cli),
    ("imports_council", test_imports_council),
    ("imports_prompting", test_imports_prompting),
    ("imports_deploy", test_imports_deploy),
    ("resource_name", test_resource_name),
    ("json_serial", test_json_serialization),
    ("memory_gc", test_memory_gc),
]

def run_single_test(test_id, stats):
    """Run a single random test."""
    name, func = random.choice(ALL_TESTS)
    start = time.time()
    
    try:
        result = func()
        duration = time.time() - start
        stats.record(name, True, duration)
        return True, name, duration
    except Exception as e:
        duration = time.time() - start
        stats.record(name, False, duration, e)
        return False, name, str(e)

def main():
    MAX_TESTS = 500
    MAX_DURATION = 30 * 60  # 30 minutes
    WORKERS = 5  # Parallel
    
    print("=" * 70)
    print("BANDIT CLI COMPONENT STRESS TEST")
    print(f"Target: {MAX_TESTS} checks over {MAX_DURATION//60} minutes")
    print(f"Workers: {WORKERS}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    stats = Stats()
    start_time = time.time()
    completed = 0
    
    with ThreadPoolExecutor(max_workers=WORKERS) as executor:
        futures = [executor.submit(run_single_test, i, stats) for i in range(MAX_TESTS)]
        
        for future in as_completed(futures):
            completed += 1
            elapsed = time.time() - start_time
            
            if elapsed > MAX_DURATION:
                print(f"\n⏰ Time limit reached")
                break
            
            try:
                success, name, result = future.result()
                
                if completed % 50 == 0:
                    rate = completed / elapsed if elapsed > 0 else 0
                    print(f"[{completed}/{MAX_TESTS}] Pass: {stats.passed} | Fail: {stats.failed} | "
                          f"Rate: {rate:.1f}/sec | Elapsed: {elapsed:.1f}s")
                          
            except Exception as e:
                print(f"[{completed}] Exception: {e}")
    
    # Results
    elapsed = time.time() - start_time
    total = stats.passed + stats.failed
    
    print("\n" + "=" * 70)
    print("FINAL RESULTS")
    print("=" * 70)
    print(f"Total: {total}")
    print(f"Passed: {stats.passed} ({stats.passed/total*100:.1f}%)")
    print(f"Failed: {stats.failed}")
    print(f"Duration: {elapsed:.1f}s ({elapsed/60:.1f} min)")
    print(f"Rate: {total/elapsed:.1f} tests/sec")
    
    print("\nBy Category:")
    for cat, times in sorted(stats.category_times.items()):
        avg = sum(times)/len(times) if times else 0
        print(f"  {cat}: {len(times)} tests, avg {avg*1000:.2f}ms")
    
    if stats.errors:
        print(f"\nErrors ({len(stats.errors)}):")
        for err in stats.errors[:10]:
            print(f"  - [{err['cat']}] {err['err']}")
    
    # Save
    with open("cli_stress_results.json", "w") as f:
        json.dump({
            "total": total,
            "passed": stats.passed,
            "failed": stats.failed,
            "duration": elapsed,
            "errors": stats.errors,
        }, f, indent=2)
    
    print("\nResults saved to cli_stress_results.json")
    return 0 if stats.failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
