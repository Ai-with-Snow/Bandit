import asyncio
import sys
import os
import time
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from scripts.voice_thinking import BanditVoiceEngine, SessionStats

SCENARIOS = [
    # Creative
    "Sing an original song about your favorite anime character. No playlist tracks—straight freestyle vibes.",
    "Tell me everything you do best in 2 minutes 20 seconds flat, with max details.",
    
    # Logic & Multi-Step
    "Who was the first person to step on Mars, and what year did they plant the flag?",
    "Plan a full itinerary for a cosplay con in NYC next week—include travel from Brooklyn, best photo spots, and a trap music lineup.",
    "Compare the protein in three Caribbean dishes I name: Ackee & Saltfish, Curried Goat, and Jerk Chicken. Rank 'em by nutrition and suggest a recipe mashup.",
    
    # Sarcasm & Nuance
    "Pretend you are a frustrated customer about a late cosplay wig order—what questions would you fire at support?",
    "Explain quantum computing like I'm five, but then debate if it's real or Annunaki tech.",
    
    # Contextual
    "Name three things you are grateful for besides me, then tie it to Black culture history."
]

async def run_complex_test():
    print(f"🚀 Starting Bandit v2.4.5 Complex Query Stress Test...")
    engine = BanditVoiceEngine()
    
    # Mock Mic for automated run
    class MockMic:
        def __init__(self, stats): self.stats = stats; self.connected = True; self.device_name = "Mock Virtual"
        def get_current_rms(self): return 10 # Low enough to not barge-in
        def listen_until_silence(self, *args): return b""
        def close(self): pass
    
    engine.mic = MockMic(engine.stats)
    engine.tts.mic = engine.mic # Link for barge-in checks
    
    for i, prompt in enumerate(SCENARIOS, 1):
        print(f"\n────────────────────────────────────────────────────────────────────────────────")
        print(f"🧪 TEST CASE {i}/{len(SCENARIOS)}")
        print(f"📥 PROMPT: {prompt}")
        print(f"────────────────────────────────────────────────────────────────────────────────")
        
        t0 = time.time()
        # Simulation: Set UI status
        engine.ui.set_status(f"Processing Test Case {i}...")
        
        # Core Logic
        reply, req_deep, deep = await engine.convo.route_and_respond(prompt)
        
        # VOCAL VERIFICATION: Speak the response
        print(f"🎙️ Speaking response...")
        await engine.tts.speak(reply)
        
        latency = time.time() - t0
        engine.stats.turns += 1
        engine.stats.last_latency = latency
        
        print(f"🧠 BRAIN: {'DEEP' if req_deep else 'FAST'}")
        print(f"⏱️ LATENCY: {latency:.2f}s")
        print(f"🎭 REPLY: {reply[:200]}...")
        if deep:
            print(f"🔍 DEEP REASONING: {deep[:200]}...")
            
        # Verify Dialogue Isolation (simplified check)
        if "Thinking:" in reply or "Analysis:" in reply:
             print("❌ WARNING: Internal thoughts leaked into reply!")
        else:
             print("✅ DIALOGUE ISOLATION: Clean")
             
        await asyncio.sleep(1) # Cool down

    print(f"\n🏆 TEST COMPLETE: All scenarios processed.")

if __name__ == "__main__":
    asyncio.run(run_complex_test())
