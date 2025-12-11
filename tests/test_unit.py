"""Unit tests for Bandit components - no subprocess needed.

Tests the core functionality without the interactive CLI.
"""

import sys
import os

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from datetime import datetime
from pathlib import Path

# Test results
results = {"passed": 0, "failed": 0, "errors": []}

def test(name):
    """Decorator for tests."""
    def decorator(func):
        def wrapper():
            try:
                func()
                results["passed"] += 1
                print(f"  ✅ {name}")
                return True
            except AssertionError as e:
                results["failed"] += 1
                results["errors"].append(f"{name}: {e}")
                print(f"  ❌ {name}: {e}")
                return False
            except Exception as e:
                results["failed"] += 1
                results["errors"].append(f"{name}: {type(e).__name__}: {e}")
                print(f"  ❌ {name}: {type(e).__name__}: {e}")
                return False
        return wrapper
    return decorator

# ============================================
# MEMORY MANAGER TESTS
# ============================================
print("\n📦 Testing MemoryManager...")

@test("MemoryManager instantiation")
def test_memory_init():
    from scripts.bandit_cli import MemoryManager
    m = MemoryManager("test-project")
    assert m.project_id == "test-project"
    assert m.conversation_history == []
    assert m.primer_context == ""

test_memory_init()

@test("MemoryManager add_message")
def test_memory_add():
    from scripts.bandit_cli import MemoryManager
    m = MemoryManager("test-project")
    m.add_message("user", "hello")
    m.add_message("bandit", "hi there!")
    assert len(m.conversation_history) == 2
    assert m.conversation_history[0]["role"] == "user"
    assert m.conversation_history[1]["content"] == "hi there!"

test_memory_add()

@test("MemoryManager get_context")
def test_memory_context():
    from scripts.bandit_cli import MemoryManager
    m = MemoryManager("test-project")
    m.add_message("user", "test message")
    ctx = m.get_context()
    assert "USER: test message" in ctx

test_memory_context()

@test("MemoryManager primer context integration")
def test_memory_primer():
    from scripts.bandit_cli import MemoryManager
    m = MemoryManager("test-project")
    m.primer_context = "Recent topics: coding, python"
    m.add_message("user", "hello")
    ctx = m.get_context()
    assert "[PRIMER]" in ctx
    assert "Recent topics" in ctx

test_memory_primer()

@test("MemoryManager respects SHORT_TERM_MEMORY_LIMIT")
def test_memory_limit():
    from scripts.bandit_cli import MemoryManager, SHORT_TERM_MEMORY_LIMIT
    m = MemoryManager("test-project")
    for i in range(SHORT_TERM_MEMORY_LIMIT + 100):
        m.add_message("user", f"message {i}")
    assert len(m.conversation_history) == SHORT_TERM_MEMORY_LIMIT

test_memory_limit()

# ============================================
# DEPLOY SCRIPT TESTS (without actual deploy)
# ============================================
print("\n🚀 Testing deploy_reasoning_engine components...")

@test("MODEL_COSTS defined")
def test_model_costs():
    from scripts.deploy_reasoning_engine import MODEL_COSTS
    assert "flash" in MODEL_COSTS
    assert "pro" in MODEL_COSTS
    assert "elite" in MODEL_COSTS

test_model_costs()

@test("SEARCH_KEYWORDS defined")
def test_search_keywords():
    from scripts.deploy_reasoning_engine import SEARCH_KEYWORDS
    assert "search" in SEARCH_KEYWORDS
    assert "latest" in SEARCH_KEYWORDS

test_search_keywords()

# ============================================
# COUNCIL TESTS
# ============================================
print("\n👥 Testing council module...")

@test("Council module imports")
def test_council_import():
    from scripts.council import BANDIT_PROFILE, ICEWIRE_PROFILE, CIPHER_PROFILE, run_council
    assert "Bandit" in BANDIT_PROFILE
    assert "Ice Wire" in ICEWIRE_PROFILE
    assert "Cipher" in CIPHER_PROFILE
    assert callable(run_council)

test_council_import()

@test("Council agent profiles have required content")
def test_council_profiles():
    from scripts.council import BANDIT_PROFILE, ICEWIRE_PROFILE, CIPHER_PROFILE
    # Check all profiles have identity and personality sections
    for profile in [BANDIT_PROFILE, ICEWIRE_PROFILE, CIPHER_PROFILE]:
        assert "[IDENTITY]" in profile, "Missing IDENTITY section"
        assert "[PERSONALITY]" in profile, "Missing PERSONALITY section"
        assert "[ROLE IN COUNCIL]" in profile, "Missing ROLE IN COUNCIL section"

test_council_profiles()

# ============================================
# PROMPTING TESTS
# ============================================
print("\n🧠 Testing prompting module...")

@test("Prompting module imports")
def test_prompting_import():
    from scripts.prompting import tree_of_thought, battle_of_bots, optimize_prompt
    assert callable(tree_of_thought)
    assert callable(battle_of_bots)
    assert callable(optimize_prompt)

test_prompting_import()

# ============================================
# CLI UTILITIES
# ============================================
print("\n🔧 Testing CLI utilities...")

@test("get_engine_resource_name formats correctly")
def test_resource_name():
    from scripts.bandit_cli import get_engine_resource_name
    result = get_engine_resource_name("my-project", "us-central1", "123456")
    assert result == "projects/my-project/locations/us-central1/reasoningEngines/123456"

test_resource_name()

@test("TIMEZONE is set to NY/EST")
def test_timezone():
    from scripts.bandit_cli import TIMEZONE
    assert str(TIMEZONE) == "America/New_York"

test_timezone()

@test("SHORT_TERM_MEMORY_LIMIT is 1000")
def test_memory_limit_value():
    from scripts.bandit_cli import SHORT_TERM_MEMORY_LIMIT
    assert SHORT_TERM_MEMORY_LIMIT == 1000

test_memory_limit_value()

# ============================================
# SUMMARY
# ============================================
print("\n" + "=" * 50)
print("TEST SUMMARY")
print("=" * 50)
print(f"Passed: {results['passed']}")
print(f"Failed: {results['failed']}")
print(f"Total:  {results['passed'] + results['failed']}")

if results["errors"]:
    print(f"\nErrors:")
    for err in results["errors"]:
        print(f"  - {err}")

success_rate = results['passed'] / (results['passed'] + results['failed']) * 100
print(f"\nSuccess Rate: {success_rate:.1f}%")

sys.exit(0 if results['failed'] == 0 else 1)
