"""Quick response time test for Bandit proxy."""
import time
import httpx

PROXY_URL = "http://localhost:8000/v1/chat/completions"

def test_instant():
    print("Testing instant mode with 'hi'...")
    start = time.time()
    r = httpx.post(PROXY_URL, json={
        "model": "test",
        "messages": [{"role": "user", "content": "hi"}],
        "thinking_mode": "instant"
    }, timeout=120)
    elapsed = time.time() - start
    
    data = r.json()
    print(f"Time: {elapsed:.2f}s")
    print(f"Model: {data.get('model', '?')}")
    print(f"Response: {data['choices'][0]['message']['content'][:100]}...")
    return elapsed

if __name__ == "__main__":
    test_instant()
