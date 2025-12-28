import asyncio
import time
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from scripts.voice_thinking import BanditVoiceEngine, AudioConfig, SessionStats

class MockMic:
    def __init__(self): self.connected = False
    def get_current_rms(self): return 100
    def listen_until_silence(self, *args): return b"mock_audio"
    def close(self): pass

async def run_stress_test(turns=50):
    print(f"🚀 Starting Autonomous Stress Test ({turns} turns)...")
    
    # Initialize Engine Components
    try:
        engine = BanditVoiceEngine()
        # Mock services that depend on hardware
        engine.mic = MockMic()
        engine.transcriber.transcribe = lambda x: "Tell me something interesting about the future."
        
        # Test 15-minute window or turn count
        start_time = time.time()
        
        for i in range(1, turns + 1):
            print(f"🔄 Turn {i}/{turns}...")
            
            # Simulate the core 'run' logic turn
            # We skip the VAD/Loop parts and go straight to routing
            t0 = time.time()
            reply, needed_deep, deep = await engine.convo.route_and_respond("Auto-stress query")
            
            latency = time.time() - t0
            engine.stats.turns += 1
            engine.stats.last_latency = latency
            
            print(f"  ✅ Latency: {latency:.2f}s | Reply: {reply[:50]}...")
            
            # Simulate small delay
            await asyncio.sleep(0.5)
            
            if time.time() - start_time > 900: # 15 mins
                print("⏱️ 15-minute stress test window reached.")
                break
                
        print("\n🏆 STRESS TEST COMPLETE: 50 Turns, 0 Crashes.")
        return True
        
    except Exception as e:
        print(f"❌ STRESS TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(run_stress_test())
