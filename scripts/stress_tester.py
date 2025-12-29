import asyncio
import os
import time
from typing import List
from voice_thinking import BanditVoiceEngine

async def run_stress_test():
    """
    Automated 10-turn stress test for core latency benchmarking.
    Excludes LIFX and Optimum tests to focus on routing and reasoning speed.
    """
    test_queries = [
        "What is the current time in Tokyo?",
        "Explain quantum entanglement in one sentence.",
        "Who wrote the book 'Meditations'?",
        "Translate 'I love the stars' to Japanese.",
        "What is the capital of France?",
        "How many legs does a spider have?",
        "Who is the current CEO of Google?",
        "What is the weather like in New York? (Simulated search)",
        "Tell me a short joke.",
        "What is the square root of 144?"
    ]

    print("🚀 Starting Latency Stress Test (10 Turns)...")
    print("-" * 40)
    
    engine = BanditVoiceEngine()
    latencies = []
    
    # We run the engine in a separate task so we can monitor stats
    test_task = asyncio.create_task(engine.run(test_inputs=test_queries))
    
    last_turn = 0
    while not test_task.done():
        await asyncio.sleep(1)
        if engine.stats.turns > last_turn:
            lat = engine.stats.last_latency
            latencies.append(lat)
            print(f"✅ Turn {engine.stats.turns}: {lat:.2f}s")
            last_turn = engine.stats.turns
            
        if engine.stats.turns >= len(test_queries):
            # Give it a moment to finish the last TTS/UI update
            await asyncio.sleep(2)
            break
            
    print("-" * 40)
    print("📊 Stress Test Results:")
    if latencies:
        avg_lat = sum(latencies) / len(latencies)
        max_lat = max(latencies)
        min_lat = min(latencies)
        print(f"Total Turns: {len(latencies)}")
        print(f"Avg Latency: {avg_lat:.2f}s")
        print(f"Min Latency: {min_lat:.2f}s")
        print(f"Max Latency: {max_lat:.2f}s")
    else:
        print("No latencies recorded. Test may have failed.")
    print("-" * 40)

if __name__ == "__main__":
    asyncio.run(run_stress_test())
