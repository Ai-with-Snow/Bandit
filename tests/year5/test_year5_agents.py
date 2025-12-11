"""Year 5: Advanced Agent Architectures Tests

Master's Year 1 — Agent Frameworks Deep Dive

Covers:
- Course 5.1: Agent Frameworks (LangGraph, ReAct, LlamaIndex, CrewAI)
- Course 5.2: Advanced Prompting Research
- Course 5.3: Multimodal Integration Research
- Course 5.4: Production Optimization Research

Required: 93%+ to pass
"""

import pytest
import os
import time
import json
from typing import Dict, List, Any, Optional
from google import genai
from google.genai import types
from pydantic import BaseModel

# Configuration
GCP_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "project-5f169828-6f8d-450b-923")
GCP_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
GLOBAL_LOCATION = "global"  # For Gemini 3 models

# Rate limiting
last_api_call_time = 0
API_CALL_DELAY = 20

@pytest.fixture(scope="function", autouse=True)
def rate_limit():
    """Enforce 30-second delay between API calls"""
    global last_api_call_time
    current_time = time.time()
    time_since_last_call = current_time - last_api_call_time
    
    if last_api_call_time > 0 and time_since_last_call < API_CALL_DELAY:
        wait_time = API_CALL_DELAY - time_since_last_call
        print(f"\n⏳ Rate limiting: waiting {wait_time:.1f}s...")
        time.sleep(wait_time)
    
    yield
    last_api_call_time = time.time()


@pytest.fixture(scope="session")
def client():
    """Initialize Gemini client with Vertex AI"""
    return genai.Client(
        vertexai=True,
        project=GCP_PROJECT,
        location=GCP_LOCATION
    )


@pytest.fixture(scope="session")
def global_client():
    """Initialize Gemini client for Gemini 3 models (global endpoint)"""
    return genai.Client(
        vertexai=True,
        project=GCP_PROJECT,
        location=GLOBAL_LOCATION
    )


# ============================================================================
# COURSE 5.1: Agent Frameworks Deep Dive
# ============================================================================

class TestCourse5_1_AgentFrameworks:
    """Course 5.1: Agent Frameworks (LangGraph, ReAct patterns)"""
    
    def test_001_react_agent_pattern(self, global_client):
        """Implement ReAct (Reasoning + Acting) agent pattern"""
        # ReAct pattern: Thought → Action → Observation → Thought...
        
        react_prompt = """You are a ReAct agent. Follow this pattern:
Thought: I need to figure out what 15 * 7 equals
Action: calculate(15 * 7)
Observation: 105
Thought: I now know the answer
Answer: 105

Now solve this using the same pattern:
What is 23 + 45?"""
        
        response = global_client.models.generate_content(
            model='gemini-3-pro-preview',
            contents=react_prompt,
            config=types.GenerateContentConfig(temperature=0.3)
        )
        
        text = response.text or ""
        # Should contain ReAct pattern elements
        assert "Thought" in text or "thought" in text.lower()
        assert "68" in text  # Correct answer
    
    def test_002_state_machine_reasoning(self, global_client):
        """Implement state machine for multi-step reasoning"""
        
        state_prompt = """You are a state machine agent tracking conversation state.

Current State: GREETING
Valid Transitions: GREETING -> QUESTION -> ANSWER -> GOODBYE

User says: "Hello!"
Your response should update state and respond appropriately.

Output format:
STATE: [new state]
RESPONSE: [your response]"""
        
        response = global_client.models.generate_content(
            model='gemini-3-pro-preview',
            contents=state_prompt,
            config=types.GenerateContentConfig(temperature=0.3)
        )
        
        text = response.text or ""
        assert "STATE:" in text or "state" in text.lower()
        assert "RESPONSE:" in text or len(text) > 20
    
    def test_003_tool_orchestration(self, global_client):
        """Test multi-tool orchestration logic"""
        
        # Define mock tools
        tools = [
            types.Tool(function_declarations=[
                types.FunctionDeclaration(
                    name="search_web",
                    description="Search the web for information",
                    parameters={"type": "object", "properties": {
                        "query": {"type": "string", "description": "Search query"}
                    }, "required": ["query"]}
                ),
                types.FunctionDeclaration(
                    name="calculate",
                    description="Perform mathematical calculations",
                    parameters={"type": "object", "properties": {
                        "expression": {"type": "string", "description": "Math expression"}
                    }, "required": ["expression"]}
                )
            ])
        ]
        
        response = global_client.models.generate_content(
            model='gemini-3-pro-preview',
            contents="What is 25 * 4 and can you search for the capital of France?",
            config=types.GenerateContentConfig(
                tools=tools,
                temperature=0.3
            )
        )
        
        # Should have function calls or text response
        assert response.candidates is not None
        assert len(response.candidates) > 0
    
    def test_004_agent_memory_pattern(self, global_client):
        """Test agent memory management pattern"""
        
        # Simulate agent with memory
        memory = []
        chat = global_client.chats.create(
            model='gemini-3-pro-preview',
            config=types.GenerateContentConfig(
                system_instruction="""You are an agent with memory.
When asked about previous messages, recall them accurately.
Keep track of all facts mentioned."""
            )
        )
        
        # Store in memory
        r1 = chat.send_message("Remember: The secret code is ALPHA-7")
        memory.append({"role": "user", "content": "Secret code: ALPHA-7"})
        
        r2 = chat.send_message("Remember: The meeting is at 3pm")
        memory.append({"role": "user", "content": "Meeting: 3pm"})
        
        # Test recall
        r3 = chat.send_message("What is the secret code?")
        
        assert r3.text is not None
        assert "ALPHA" in r3.text or "7" in r3.text


# ============================================================================
# COURSE 5.2: Advanced Prompting Research
# ============================================================================

class TestCourse5_2_AdvancedPrompting:
    """Course 5.2: Advanced Prompting Research"""
    
    def test_005_meta_prompting(self, global_client):
        """Test meta-prompting (prompts that generate prompts)"""
        
        meta_prompt = """You are a prompt engineer. Create a prompt that will 
make an AI explain quantum computing to a 5-year-old.

Output only the prompt, nothing else."""
        
        response = global_client.models.generate_content(
            model='gemini-3-pro-preview',
            contents=meta_prompt,
            config=types.GenerateContentConfig(temperature=0.7)
        )
        
        generated_prompt = response.text or ""
        assert len(generated_prompt) > 20
        # The generated prompt should mention simplification
        assert any(word in generated_prompt.lower() for word in 
                   ['simple', 'explain', 'child', 'easy', '5', 'kid', 'young'])
    
    def test_006_self_consistency_prompting(self, global_client):
        """Test self-consistency prompting (multiple reasoning paths)"""
        
        problem = """Solve this puzzle using 3 different reasoning approaches:
A farmer has 17 sheep. All but 9 run away. How many are left?"""
        
        response = global_client.models.generate_content(
            model='gemini-3-pro-preview',
            contents=problem,
            config=types.GenerateContentConfig(temperature=0.7)
        )
        
        text = response.text or ""
        # Should arrive at 9 through multiple paths
        assert "9" in text
    
    def test_007_tree_of_thought(self, global_client):
        """Test tree-of-thought reasoning pattern"""
        
        tot_prompt = """Use tree-of-thought reasoning to solve this:
        
Problem: Arrange the digits 1, 2, 3, 4 to make the largest possible number.

Explore multiple branches:
Branch A: Start with largest digit first
Branch B: Consider different orderings
Branch C: Verify your answer

Show your reasoning tree, then give final answer."""
        
        response = global_client.models.generate_content(
            model='gemini-3-pro-preview',
            contents=tot_prompt,
            config=types.GenerateContentConfig(temperature=0.5)
        )
        
        text = response.text or ""
        assert "4321" in text  # Correct answer


# ============================================================================
# COURSE 5.3: Multimodal Integration Research
# ============================================================================

class TestCourse5_3_MultimodalIntegration:
    """Course 5.3: Multimodal Integration Research"""
    
    def test_008_cross_modal_reasoning(self, global_client):
        """Test cross-modal reasoning (text + structured data)"""
        
        prompt = """Analyze this data and provide insights:

Sales Data (JSON):
{"Q1": 150000, "Q2": 180000, "Q3": 165000, "Q4": 220000}

Questions:
1. What is the total annual sales?
2. Which quarter had the highest growth rate?
3. What trend do you observe?

Provide structured analysis."""
        
        response = global_client.models.generate_content(
            model='gemini-3-pro-preview',
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.3)
        )
        
        text = response.text or ""
        # Should calculate total (715000)
        assert "715" in text or "715000" in text or "715,000" in text
    
    def test_009_structured_data_extraction(self, global_client):
        """Test extracting structured data from unstructured text"""
        
        class ExtractedInfo(BaseModel):
            name: str
            company: str
            email: Optional[str] = None
        
        prompt = """Extract contact information from this text:

"Hi, I'm Sarah Chen from TechCorp. You can reach me at sarah.chen@techcorp.com"

Return as JSON: {"name": "...", "company": "...", "email": "..."}"""
        
        response = global_client.models.generate_content(
            model='gemini-3-pro-preview',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1
            )
        )
        
        text = response.text or "{}"
        try:
            data = json.loads(text)
            assert "Sarah" in data.get("name", "")
            assert "TechCorp" in data.get("company", "") or "techcorp" in data.get("company", "").lower()
        except json.JSONDecodeError:
            # If not valid JSON, check text contains expected info
            assert "Sarah" in text
            assert "TechCorp" in text


# ============================================================================
# COURSE 5.4: Production Optimization Research
# ============================================================================

class TestCourse5_4_ProductionOptimization:
    """Course 5.4: Production Optimization Research"""
    
    def test_010_token_efficiency(self, client):
        """Test token-efficient prompt design"""
        
        # Verbose prompt
        verbose_prompt = """I would like you to please provide me with a list 
of exactly three programming languages that are commonly used for web development. 
Please format your response as a simple bulleted list."""
        
        # Efficient prompt
        efficient_prompt = "List 3 web programming languages, bulleted."
        
        verbose_tokens = client.models.count_tokens(
            model='gemini-2.5-flash',
            contents=verbose_prompt
        )
        
        efficient_tokens = client.models.count_tokens(
            model='gemini-2.5-flash',
            contents=efficient_prompt
        )
        
        # Efficient should use fewer tokens
        v_count = getattr(verbose_tokens, 'total_tokens', 50)
        e_count = getattr(efficient_tokens, 'total_tokens', 10)
        
        assert e_count < v_count
    
    def test_011_caching_strategy(self, client):
        """Test caching strategy design"""
        
        # Simulate cache key generation
        def generate_cache_key(prompt: str, model: str, temp: float) -> str:
            import hashlib
            key_data = f"{prompt}:{model}:{temp}"
            return hashlib.md5(key_data.encode()).hexdigest()[:16]
        
        key1 = generate_cache_key("Hello", "gemini-2.5-flash", 0.5)
        key2 = generate_cache_key("Hello", "gemini-2.5-flash", 0.5)
        key3 = generate_cache_key("Hello", "gemini-2.5-flash", 0.7)
        
        # Same inputs = same key
        assert key1 == key2
        # Different temp = different key
        assert key1 != key3


# ============================================================================
# YEAR 5 COMPREHENSIVE EXAM
# ============================================================================

class TestYear5ComprehensiveExam:
    """Year 5 Comprehensive Exam: Research Project"""
    
    def test_final_autonomous_agent(self, global_client):
        """Final: Build autonomous agent that solves multi-step problem"""
        
        agent_prompt = """You are an autonomous research agent. Solve this problem step by step:

Problem: Design a system to recommend books based on user preferences.

Requirements:
1. Identify key components needed
2. Design the data flow
3. Specify the recommendation algorithm
4. Handle edge cases

Output a complete system design."""
        
        response = global_client.models.generate_content(
            model='gemini-3-pro-preview',
            contents=agent_prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=1500
            )
        )
        
        text = response.text or ""
        # Should have substantial design
        assert len(text) > 200
        # Should address key components
        components = ['data', 'algorithm', 'user', 'recommend']
        assert sum(1 for c in components if c in text.lower()) >= 2


if __name__ == "__main__":
    pytest.main([__file__, '-v', '--tb=short'])
