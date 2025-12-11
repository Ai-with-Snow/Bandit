"""
BANDIT YEAR 3: DEEP REASONING
Course 3.3 Automated Tests

Models: gemini-3-pro-preview
Goals:
1. Verify "Thinking" / Chain of Thought capabilities
2. Solve Complex Logic Puzzles requiring multi-step reasoning
"""

import pytest
import os
import time
from google import genai
from google.genai import types

# Test Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GCP_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "project-5f169828-6f8d-450b-923")

client = None
last_api_call_time = 0
API_CALL_DELAY = 15 # Longer delay for thinking models

@pytest.fixture(scope="session", autouse=True)
def setup_client():
    global client
    if GEMINI_API_KEY:
        client = genai.Client(api_key=GEMINI_API_KEY)
    else:
        try:
            client = genai.Client(
                vertexai=True,
                project=GCP_PROJECT,
                location='global' 
            )
        except Exception:
             client = genai.Client(
                vertexai=True,
                project=GCP_PROJECT,
                location='us-central1' 
            )

@pytest.fixture(scope="function", autouse=True)
def rate_limit():
    global last_api_call_time
    current_time = time.time()
    if last_api_call_time > 0:
        elapsed = current_time - last_api_call_time
        if elapsed < API_CALL_DELAY:
            time.sleep(API_CALL_DELAY - elapsed)
    yield
    last_api_call_time = time.time()

class TestCourse3_3_Reasoning:
    """Mastery of Deep Reasoning with Gemini 3"""

    def test_001_logic_puzzle(self):
        """Week 10: Complex Logic Puzzle"""
        prompt = """
        Solve this logic puzzle:
        Three people (Alice, Bob, Charlie) ordered three different drinks (Coffee, Tea, Soda) and are wearing three different colored shirts (Red, Blue, Green).
        1. Alice is not wearing Red and didn't order Soda.
        2. The person in Blue ordered Tea.
        3. Bob ordered Coffee.
        Who ordered what and is wearing which color? Let's think step by step.
        """
        
        response = client.models.generate_content(
            model='gemini-3-pro-preview',
            contents=prompt
        )
        
        text = response.text.lower()
        # Verify correctness
        # Bob=Coffee (Given). Person-Blue=Tea. So Bob is NOT Blue (since he ordered coffee).
        # Alice != Red. Alice != Soda. 
        # If Bob=Coffee, Person-Blue=Tea -> Charlie=Soda? or Alice=Tea?
        # If Person-Blue = Tea
        # Alice didn't order Soda. Bob ordered Coffee. So Alice MUST be the one who ordered Tea (since Bob has coffee).
        # Therefore Alice = Tea. And since Person-Blue=Tea, Alice = Blue.
        # Bob = Coffee. Bob != Blue. Alice=Blue. So Bob is Red or Green.
        # Alice is not Red (Condition 1). Alice is Blue (Derived). Correct.
        # Remaining: Charlie ordered Soda.
        # Current State: Alice(Blue, Tea), Bob(Coffee, ?), Charlie(Soda, ?)
        # Colors left: Red, Green.
        # No other constraints given in truncated prompt? 
        # Actually logic is deducible.
        
        assert "alice" in text and "blue" in text
        assert "bob" in text and "coffee" in text
        assert "charlie" in text and "soda" in text

    def test_002_math_reasoning(self):
        """Week 12: Multi-step Math"""
        prompt = "Calculate the sum of the first 10 prime numbers, then multiply by 2."
        # Primes: 2, 3, 5, 7, 11, 13, 17, 19, 23, 29
        # Sum = 129. * 2 = 258.
        
        response = client.models.generate_content(
            model='gemini-3-pro-preview',
            contents=prompt
        )
        
        assert "258" in response.text

if __name__ == "__main__":
    pytest.main([__file__])
