"""Live Complex Questions Test - 50 questions.

Tests Bandit with 50 complex questions that require deep reasoning.
"""

import sys
import os
import time
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.bandit_cli import (
    get_engine_resource_name,
    _load_credentials,
    DEFAULT_PROJECT,
    DEFAULT_LOCATION,
    DEFAULT_ENGINE_ID,
)
import requests

COMPLEX_QUESTIONS = [
    # Architecture & Design
    "Design a microservices architecture for a real-time stock trading platform",
    "How would you implement a distributed cache system for a global CDN",
    "Explain the trade-offs between event sourcing and CRUD patterns",
    "Design a recommendation engine for a streaming music service",
    "How would you architect a multi-tenant SaaS platform",
    
    # AI & ML
    "Explain transformer architecture and attention mechanisms",
    "How do you prevent catastrophic forgetting in continual learning",
    "Compare LoRA vs full fine-tuning for LLM adaptation",
    "Design a RAG system for enterprise document search",
    "Explain RLHF and its role in aligning language models",
    
    # Distributed Systems
    "How does Raft consensus algorithm handle network partitions",
    "Explain CAP theorem with real-world database examples",
    "Design a globally distributed payment processing system",
    "How would you implement exactly-once semantics in a message queue",
    "Explain vector clocks and their use in distributed systems",
    
    # Security
    "Design a zero-trust security architecture for a cloud platform",
    "Explain OAuth 2.0 and PKCE flow for mobile applications",
    "How would you implement end-to-end encryption for a messaging app",
    "Design an API rate limiting system that prevents DDoS attacks",
    "Explain JWT vs session-based authentication trade-offs",
    
    # Performance
    "How would you optimize a PostgreSQL database with 1 billion rows",
    "Design a caching strategy for a high-traffic e-commerce site",
    "Explain memory management in Go vs Rust",
    "How would you profile and optimize a Python ML pipeline",
    "Design a load balancing strategy for websocket connections",
    
    # Cloud & Infrastructure
    "Compare Kubernetes vs serverless for a batch processing workload",
    "Design a disaster recovery strategy for a multi-region application",
    "How would you implement GitOps for infrastructure management",
    "Explain service mesh architecture and when to use it",
    "Design a cost-optimization strategy for cloud infrastructure",
    
    # Data Engineering
    "Design a real-time data pipeline for IoT sensor data",
    "Compare Apache Kafka vs Pulsar for event streaming",
    "How would you implement data lineage tracking at scale",
    "Design a data lake architecture for petabyte-scale analytics",
    "Explain CDC (Change Data Capture) patterns and implementations",
    
    # Software Engineering
    "How do you balance technical debt vs feature development",
    "Design a feature flag system for gradual rollouts",
    "Explain trunk-based development vs GitFlow",
    "How would you implement a plugin architecture in Python",
    "Design an observability stack for microservices",
    
    # Problem Solving
    "How would you debug a memory leak in a production system",
    "Design a system for detecting anomalies in user behavior",
    "How would you migrate a monolith to microservices incrementally",
    "Explain strategies for handling thundering herd problems",
    "Design a queue-based system for handling bursty traffic",
    
    # Strategy
    "How would you evaluate build vs buy for a core platform component",
    "Design a testing strategy for a safety-critical autonomous system",
    "Explain the 12-factor app methodology and its relevance today",
    "How would you plan a database migration with zero downtime",
    "Design an A/B testing framework for ML models",
]

def query(prompt: str, timeout: int = 120) -> dict:
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
        response = requests.post(api_endpoint, headers=headers, json=payload, timeout=timeout)
        duration = time.time() - start
        
        if response.status_code == 200:
            result = response.json()
            return {"success": True, "response": result.get("output", "")[:500], "duration": duration}
        else:
            return {"success": False, "error": f"HTTP {response.status_code}", "duration": duration}
    except requests.exceptions.Timeout:
        return {"success": False, "error": "TIMEOUT", "duration": time.time() - start}
    except Exception as e:
        return {"success": False, "error": str(e)[:100], "duration": time.time() - start}

def main():
    print("=" * 70)
    print("LIVE COMPLEX QUESTIONS TEST - 50 QUESTIONS")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    passed = 0
    failed = 0
    durations = []
    
    for i, q in enumerate(COMPLEX_QUESTIONS[:50]):
        print(f"\n[{i+1}/50] {q[:60]}...")
        
        result = query(q)
        durations.append(result["duration"])
        
        if result["success"]:
            passed += 1
            print(f"  ✅ ({result['duration']:.1f}s)")
            print(f"  📝 {result['response'][:150]}...")
        else:
            failed += 1
            print(f"  ❌ {result['error']}")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Passed: {passed}/50 ({passed/50*100:.0f}%)")
    print(f"Failed: {failed}")
    print(f"Avg Response Time: {sum(durations)/len(durations):.1f}s")
    print(f"Total Time: {sum(durations):.1f}s")
    
    with open("complex_questions_results.json", "w") as f:
        json.dump({"passed": passed, "failed": failed, "avg_duration": sum(durations)/len(durations)}, f, indent=2)
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
