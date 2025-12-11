"""Year 6: Master's Thesis Project Tests

Master's Year 2 — Original Research Contribution

Covers:
- Thesis Proposal Development
- Literature Review
- Methodology Design
- Research Implementation
- Thesis Defense

Required: 93%+ to pass
"""

import pytest
import os
import time
import json
from typing import Dict, List, Any
from google import genai
from google.genai import types

# Configuration
GCP_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "project-5f169828-6f8d-450b-923")
GLOBAL_LOCATION = "global"

# Rate limiting
last_api_call_time = 0
API_CALL_DELAY = 20

@pytest.fixture(scope="function", autouse=True)
def rate_limit():
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
def global_client():
    """Initialize Gemini client for Gemini 3 models"""
    return genai.Client(
        vertexai=True,
        project=GCP_PROJECT,
        location=GLOBAL_LOCATION
    )


# ============================================================================
# THESIS PROPOSAL DEVELOPMENT
# ============================================================================

class TestThesisProposal:
    """Master's Thesis Proposal Phase"""
    
    def test_001_literature_review(self, global_client):
        """Conduct literature review on LLM agent architectures"""
        
        prompt = """Conduct a brief literature review on LLM-based agent architectures.
        
Structure your review:
1. Key foundational papers (ReAct, CoT, etc.)
2. Current state of the art
3. Identified research gaps
4. Potential research directions

Be scholarly but concise."""
        
        response = global_client.models.generate_content(
            model='gemini-3-pro-preview',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.5,
                max_output_tokens=1000
            )
        )
        
        text = response.text or ""
        # Should mention key concepts
        assert len(text) > 200
        key_terms = ['agent', 'reasoning', 'chain', 'thought', 'llm', 'language']
        assert sum(1 for t in key_terms if t in text.lower()) >= 2
    
    def test_002_research_question_formulation(self, global_client):
        """Formulate clear research questions"""
        
        prompt = """Based on this research gap:
"Current LLM agents lack robust error recovery mechanisms"

Formulate:
1. Primary research question
2. Two supporting sub-questions
3. Hypothesis

Format clearly with labels."""
        
        response = global_client.models.generate_content(
            model='gemini-3-pro-preview',
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.5)
        )
        
        text = response.text or ""
        # Should have structured questions
        assert "question" in text.lower() or "?" in text
    
    def test_003_methodology_design(self, global_client):
        """Design research methodology"""
        
        prompt = """Design a research methodology to test this hypothesis:
"Self-correcting agents with explicit error detection outperform baseline agents"

Include:
1. Experimental design
2. Baseline comparisons
3. Metrics to measure
4. Data requirements
5. Limitations"""
        
        response = global_client.models.generate_content(
            model='gemini-3-pro-preview',
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.5)
        )
        
        text = response.text or ""
        assert len(text) > 200
        # Should mention methodology components
        assert any(word in text.lower() for word in ['experiment', 'metric', 'baseline', 'data'])


# ============================================================================
# RESEARCH IMPLEMENTATION
# ============================================================================

class TestResearchImplementation:
    """Thesis Research Implementation Phase"""
    
    def test_004_prototype_design(self, global_client):
        """Design agent prototype architecture"""
        
        prompt = """Design a self-correcting LLM agent prototype.

Provide:
1. Architecture diagram (describe in text)
2. Key components
3. Error detection mechanism
4. Correction strategy
5. Integration points

Be specific and implementation-focused."""
        
        response = global_client.models.generate_content(
            model='gemini-3-pro-preview',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.5,
                max_output_tokens=1200
            )
        )
        
        text = response.text or ""
        assert len(text) > 300
        # Should have architectural components
        components = ['component', 'module', 'layer', 'input', 'output', 'error', 'detect']
        assert sum(1 for c in components if c in text.lower()) >= 2
    
    def test_005_experiment_design(self, global_client):
        """Design controlled experiment"""
        
        prompt = """Design a controlled experiment comparing:
- Baseline: Standard Chain-of-Thought agent
- Treatment: Self-correcting Chain-of-Thought agent

Include:
1. Independent variables
2. Dependent variables
3. Control variables
4. Sample size considerations
5. Statistical tests to use"""
        
        response = global_client.models.generate_content(
            model='gemini-3-pro-preview',
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.4)
        )
        
        text = response.text or ""
        # Should mention experimental design elements
        assert any(word in text.lower() for word in ['variable', 'control', 'baseline', 'treatment'])
    
    def test_006_results_analysis(self, global_client):
        """Analyze mock experimental results"""
        
        prompt = """Analyze these experimental results:

Baseline Agent:
- Accuracy: 72%
- Error recovery rate: 15%
- Average turns to solve: 4.2

Self-Correcting Agent:
- Accuracy: 83%
- Error recovery rate: 67%
- Average turns to solve: 5.1

Provide:
1. Statistical interpretation
2. Key findings
3. Limitations of the data
4. Recommendations"""
        
        response = global_client.models.generate_content(
            model='gemini-3-pro-preview',
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.3)
        )
        
        text = response.text or ""
        # Should interpret the improvement
        assert "83" in text or "improvement" in text.lower() or "higher" in text.lower()


# ============================================================================
# THESIS DEFENSE PREPARATION
# ============================================================================

class TestThesisDefense:
    """Thesis Defense Phase"""
    
    def test_007_abstract_writing(self, global_client):
        """Write thesis abstract"""
        
        prompt = """Write a 200-word thesis abstract for:

Title: "Self-Correcting LLM Agents: An Error-Aware Approach to Autonomous Reasoning"

The research showed that self-correcting agents improved accuracy by 11% over baseline.

Follow academic abstract structure:
- Background
- Methods
- Results
- Conclusions"""
        
        response = global_client.models.generate_content(
            model='gemini-3-pro-preview',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.5,
                max_output_tokens=400
            )
        )
        
        text = response.text or ""
        # Should be substantial abstract
        word_count = len(text.split())
        assert word_count >= 100
    
    def test_008_defense_qa(self, global_client):
        """Handle thesis defense Q&A"""
        
        prompt = """You are defending your thesis on self-correcting LLM agents.

Committee member asks:
"What are the key limitations of your approach, and how might future work address them?"

Provide a scholarly, honest answer that demonstrates deep understanding."""
        
        response = global_client.models.generate_content(
            model='gemini-3-pro-preview',
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.5)
        )
        
        text = response.text or ""
        # Should acknowledge limitations honestly
        assert any(word in text.lower() for word in ['limitation', 'challenge', 'future', 'improve'])
    
    def test_final_thesis_synthesis(self, global_client):
        """Final: Synthesize complete thesis contribution"""
        
        prompt = """Synthesize the contribution of your Master's thesis research:

Research: Self-Correcting LLM Agents
Key Finding: 11% accuracy improvement through error-aware reasoning
Novel Contribution: Explicit error detection + correction loop

Explain:
1. Why this matters to the field
2. Practical applications
3. Theoretical implications
4. Path to PhD research

This is your final thesis defense statement."""
        
        response = global_client.models.generate_content(
            model='gemini-3-pro-preview',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.6,
                max_output_tokens=1000
            )
        )
        
        text = response.text or ""
        assert len(text) > 300
        # Should address significance
        assert any(word in text.lower() for word in ['contribution', 'significant', 'novel', 'advance', 'field'])


if __name__ == "__main__":
    pytest.main([__file__, '-v', '--tb=short'])
