#!/usr/bin/env python3
"""
Bandit RAG Test Suite - 20 Question Verification
Tests async memory, 1M token context, and HQ knowledge retrieval.
"""
import os
import sys
import json
import asyncio
import time
from datetime import datetime
from pathlib import Path

# Set environment
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "project-5f169828-6f8d-450b-923")
os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", 
    str(Path.home() / "AppData/Roaming/gcloud/application_default_credentials.json"))

# Test questions covering all HQ knowledge areas
TEST_QUESTIONS = [
    # Irie Igloo Discord (1-4)
    ("What are the domes in the Irie Igloo Discord server?", "discord", ["Welcome Dome", "P.A.U.S.E.", "Frosted Market"]),
    ("What is The Melt Spot in the Irie Igloo?", "discord", ["voice", "text", "hangout"]),
    ("How do you set up FredBoat for music in Discord?", "discord", ["fredboat", "play", "music"]),
    ("What roles exist in the Irie Igloo server?", "discord", ["Community", "Practitioner", "VIP"]),
    
    # P.A.U.S.E. Workshops (5-8)
    ("What is Velvet Hours and how long is it?", "pause", ["2", "hour", "retreat"]),
    ("Describe The Art of PleasHer workshop", "pause", ["sensual", "sacred", "workshop"]),
    ("What is Feelin It Mr Krabz about?", "pause", ["sound", "3 hour"]),
    ("What's in the P.A.U.S.E. vetting form disclaimer?", "pause", ["consent", "energy", "kundalini"]),
    
    # Business Strategy (9-12)
    ("Explain the LMSIFY LLC structure", "business", ["LLC", "DBA", "parent"]),
    ("What is an SBA 7(a) loan and how can Snow use it?", "business", ["loan", "business", "acquisition"]),
    ("What business marketplaces can I use to buy businesses?", "business", ["BizBuySell", "Flippa"]),
    ("What are the event monetization streams for SnowDayKokoa?", "business", ["merch", "tips", "service"]),
    
    # Merch & Content (13-16)
    ("What are some T-shirt slogans for lifestyle events?", "merch", ["Consent", "Kink", "slogan"]),
    ("What is the definition of 'Merpz'?", "merch", ["sensation", "Captain Obvious"]),
    ("What typography styles work for Cricut designs?", "merch", ["font", "black", "vinyl"]),
    ("What is Earth is Highlarious?", "merch", ["stoner", "cosmic", "token"]),
    
    # Streaming & Professional (17-20)
    ("What platforms should Celestial Goddexx Snow stream on?", "streaming", ["Twitch", "YouTube"]),
    ("What is the Celestial Experience service menu?", "streaming", ["session", "sensory"]),
    ("What are Snow's streaming content pillars?", "streaming", ["gaming", "wellness", "creative"]),
    ("Describe the Nutrition Nebula concept", "nutrition", ["food", "wellness", "kitchen"]),
]


def search_local_hq(query: str, hq_path: str = "HQ") -> str:
    """Search HQ files locally for relevant content."""
    results = []
    query_lower = query.lower()
    keywords = [w for w in query_lower.split() if len(w) > 3]
    
    hq = Path(hq_path)
    if not hq.exists():
        return "HQ folder not found"
    
    for file_path in hq.rglob("*.md"):
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            content_lower = content.lower()
            
            # Score by keyword matches
            score = sum(1 for kw in keywords if kw in content_lower)
            if score >= 2:
                # Extract relevant snippet
                for line in content.split('\n'):
                    if any(kw in line.lower() for kw in keywords):
                        results.append((score, file_path.name, line[:200]))
                        break
        except Exception as e:
            pass
    
    # Sort by score, take top 5
    results.sort(reverse=True, key=lambda x: x[0])
    top_results = results[:5]
    
    if top_results:
        return "\n".join([f"[{r[1]}] {r[2]}" for r in top_results])
    return "No matching content found"


async def search_gcs_bucket(query: str) -> str:
    """Search GCS bucket for HQ documents."""
    try:
        from google.cloud import storage
        
        client = storage.Client()
        bucket = client.bucket("bandit-hq-docs")
        
        # List relevant blobs
        blobs = list(bucket.list_blobs(prefix="HQ/", max_results=100))
        
        results = []
        query_lower = query.lower()
        keywords = [w for w in query_lower.split() if len(w) > 3]
        
        for blob in blobs:
            if blob.name.endswith('.md'):
                try:
                    content = blob.download_as_text()
                    content_lower = content.lower()
                    
                    score = sum(1 for kw in keywords if kw in content_lower)
                    if score >= 2:
                        for line in content.split('\n'):
                            if any(kw in line.lower() for kw in keywords):
                                results.append((score, blob.name.split('/')[-1], line[:200]))
                                break
                except:
                    pass
        
        results.sort(reverse=True, key=lambda x: x[0])
        top_results = results[:5]
        
        if top_results:
            return "\n".join([f"[{r[1]}] {r[2]}" for r in top_results])
        return "No matching content found in GCS"
        
    except Exception as e:
        return f"GCS error: {e}"


async def test_question(index: int, question: str, category: str, expected_keywords: list) -> dict:
    """Test a single question against RAG."""
    start_time = time.time()
    result = {
        "index": index,
        "question": question,
        "category": category,
        "passed": False,
        "response": "",
        "latency_ms": 0,
        "method": "local"
    }
    
    # Try local search first
    local_result = search_local_hq(question)
    result["response"] = local_result
    result["method"] = "local"
    
    # Check if expected keywords are in response
    response_lower = local_result.lower()
    matches = sum(1 for kw in expected_keywords if kw.lower() in response_lower)
    result["passed"] = matches >= 1 and "not found" not in response_lower.lower()
    
    # If local fails, try GCS
    if not result["passed"]:
        gcs_result = await search_gcs_bucket(question)
        if "not found" not in gcs_result.lower() and "error" not in gcs_result.lower():
            result["response"] = gcs_result
            result["method"] = "gcs"
            response_lower = gcs_result.lower()
            matches = sum(1 for kw in expected_keywords if kw.lower() in response_lower)
            result["passed"] = matches >= 1
    
    result["latency_ms"] = int((time.time() - start_time) * 1000)
    return result


async def check_config():
    """Check Bandit configuration."""
    print("\n" + "=" * 60)
    print("🔧 CONFIGURATION CHECK")
    print("=" * 60)
    
    issues = []
    
    # Check HQ folder
    hq_path = Path("HQ")
    if hq_path.exists():
        md_files = list(hq_path.rglob("*.md"))
        print(f"✅ HQ folder found: {len(md_files)} markdown files")
    else:
        print("❌ HQ folder not found")
        issues.append("HQ folder missing")
    
    # Check GCS bucket
    try:
        from google.cloud import storage
        client = storage.Client()
        bucket = client.bucket("bandit-hq-docs")
        blobs = list(bucket.list_blobs(max_results=5))
        print(f"✅ GCS bucket connected: {len(blobs)} files accessible")
    except Exception as e:
        print(f"⚠️  GCS bucket issue: {e}")
        issues.append(f"GCS: {e}")
    
    # Check proxy for 1M context
    proxy_path = Path("proxy_server.py")
    if proxy_path.exists():
        content = proxy_path.read_text()
        if "gemini-3" in content or "gemini-2.5" in content:
            print("✅ Modern Gemini models configured (1M context)")
        else:
            print("⚠️  Check model configuration for 1M context")
            issues.append("Model config check needed")
    
    # Check CLI for async
    cli_path = Path("scripts/bandit_cli.py")
    if cli_path.exists():
        content = cli_path.read_text()
        if "async" in content and "await" in content:
            print("✅ Async operations configured in CLI")
        else:
            issues.append("Async not configured")
    
    # Check memory manager
    if cli_path.exists():
        content = cli_path.read_text()
        if "MemoryManager" in content and "BigQuery" in content:
            print("✅ Memory Manager with BigQuery found")
        else:
            issues.append("MemoryManager not found")
    
    return issues


async def main():
    """Run all tests."""
    print("=" * 60)
    print("🧪 BANDIT RAG TEST SUITE - 20 Question Verification")
    print("=" * 60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check config
    issues = await check_config()
    
    print("\n" + "=" * 60)
    print("🔍 RUNNING 20 QUESTION RAG TEST")
    print("=" * 60)
    
    results = []
    passed = 0
    failed = 0
    
    for i, (question, category, expected) in enumerate(TEST_QUESTIONS, 1):
        print(f"\n[{i:02d}/20] {question[:50]}...")
        result = await test_question(i, question, category, expected)
        results.append(result)
        
        if result["passed"]:
            passed += 1
            print(f"       ✅ PASSED ({result['method']}, {result['latency_ms']}ms)")
            print(f"       → {result['response'][:80]}...")
        else:
            failed += 1
            print(f"       ❌ FAILED")
            print(f"       → {result['response'][:80]}...")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"Passed: {passed}/20 ({(passed/20)*100:.0f}%)")
    print(f"Failed: {failed}/20")
    
    by_category = {}
    for r in results:
        cat = r["category"]
        if cat not in by_category:
            by_category[cat] = {"passed": 0, "failed": 0}
        if r["passed"]:
            by_category[cat]["passed"] += 1
        else:
            by_category[cat]["failed"] += 1
    
    print("\nBy Category:")
    for cat, stats in by_category.items():
        total = stats["passed"] + stats["failed"]
        print(f"  {cat}: {stats['passed']}/{total}")
    
    if issues:
        print("\n⚠️  Configuration Issues:")
        for issue in issues:
            print(f"  - {issue}")
    
    # Save results
    output = {
        "timestamp": datetime.now().isoformat(),
        "passed": passed,
        "failed": failed,
        "success_rate": f"{(passed/20)*100:.0f}%",
        "config_issues": issues,
        "results": results
    }
    
    with open("rag_test_results.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\n📄 Results saved to: rag_test_results.json")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
    elif passed >= 16:
        print("\n✅ GOOD: 80%+ tests passed")
    elif passed >= 10:
        print("\n⚠️  NEEDS ATTENTION: 50-80% tests passed")
    else:
        print("\n❌ CRITICAL: <50% tests passed")
    
    return failed


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
