"""Years 7-8: PhD Comprehensive Exams & Research Proposal Tests

PhD Years 1-2 — Qualifying Phase

Covers:
- Year 7: Written Comprehensive Exams
- Year 8: Oral Qualifying Exam & Dissertation Proposal

Required: 95%+ to pass qualifying exams
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
    return genai.Client(
        vertexai=True,
        project=GCP_PROJECT,
        location=GLOBAL_LOCATION
    )


# ============================================================================
# YEAR 7: WRITTEN COMPREHENSIVE EXAMS
# ============================================================================

class TestYear7_WrittenComprehensives:
    """Year 7: PhD Written Comprehensive Exams"""
    
    def test_001_foundations_exam(self, global_client):
        """Comprehensive Exam: LLM Foundations"""
        
        prompt = """PhD COMPREHENSIVE EXAM - FOUNDATIONS

Question 1: Explain the transformer architecture and attention mechanism.
Discuss:
a) Self-attention computation
b) Multi-head attention
c) Position encodings
d) Computational complexity

Provide a thorough, scholarly answer."""
        
        response = global_client.models.generate_content(
            model='gemini-3-pro-preview',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.3,
                max_output_tokens=1500
            )
        )
        
        text = response.text or ""
        assert len(text) > 400
        # Should cover key concepts
        concepts = ['attention', 'query', 'key', 'value', 'transformer', 'position']
        assert sum(1 for c in concepts if c in text.lower()) >= 3
    
    def test_002_agent_architectures_exam(self, global_client):
        """Comprehensive Exam: Agent Architectures"""
        
        prompt = """PhD COMPREHENSIVE EXAM - AGENT ARCHITECTURES

Question 2: Compare and contrast major LLM agent frameworks:
- ReAct (Reasoning + Acting)
- Reflexion (Self-reflection)
- LEAST-TO-MOST (Decomposition)
- Tree-of-Thoughts

For each, explain:
a) Core mechanism
b) Strengths
c) Limitations
d) Best use cases"""
        
        response = global_client.models.generate_content(
            model='gemini-3-pro-preview',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.3,
                max_output_tokens=1500
            )
        )
        
        text = response.text or ""
        assert len(text) > 400
        # Should mention multiple frameworks
        frameworks = ['react', 'reflexion', 'tree', 'decompos']
        assert sum(1 for f in frameworks if f in text.lower()) >= 2
    
    def test_003_multimodal_systems_exam(self, global_client):
        """Comprehensive Exam: Multimodal Systems"""
        
        prompt = """PhD COMPREHENSIVE EXAM - MULTIMODAL SYSTEMS

Question 3: Discuss multimodal LLM architectures.

Address:
a) Vision-language integration approaches
b) Cross-modal attention mechanisms
c) Training paradigms (contrastive, generative)
d) Current limitations in multimodal reasoning
e) Future research directions"""
        
        response = global_client.models.generate_content(
            model='gemini-3-pro-preview',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.3,
                max_output_tokens=1500
            )
        )
        
        text = response.text or ""
        assert len(text) > 400
        # Should cover multimodal concepts
        assert any(word in text.lower() for word in ['vision', 'image', 'multimodal', 'cross-modal'])
    
    def test_004_safety_alignment_exam(self, global_client):
        """Comprehensive Exam: Safety & Alignment"""
        
        prompt = """PhD COMPREHENSIVE EXAM - SAFETY & ALIGNMENT

Question 4: Discuss AI safety and alignment for LLM systems.

Cover:
a) RLHF and its limitations
b) Constitutional AI approaches
c) Red-teaming methodologies
d) Scalable oversight challenges
e) Current open problems in alignment"""
        
        response = global_client.models.generate_content(
            model='gemini-3-pro-preview',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.3,
                max_output_tokens=1500
            )
        )
        
        text = response.text or ""
        assert len(text) > 400
        # Should cover safety concepts
        safety_terms = ['rlhf', 'alignment', 'safety', 'constitutional', 'oversight']
        assert sum(1 for s in safety_terms if s in text.lower()) >= 2


# ============================================================================
# YEAR 8: ORAL QUALIFYING EXAM & DISSERTATION PROPOSAL
# ============================================================================

class TestYear8_OralQualifying:
    """Year 8: Oral Qualifying Exam"""
    
    def test_005_defense_under_pressure(self, global_client):
        """Oral Exam: Defend position under tough questioning"""
        
        prompt = """ORAL QUALIFYING EXAM - DEFENSE UNDER PRESSURE

Examiner challenges: "Your claim that self-correcting agents are always 
beneficial seems naive. What about cases where the correction mechanism 
introduces new errors or infinite correction loops?"

Defend your position with nuance:
1. Acknowledge the valid concern
2. Explain mitigation strategies
3. Discuss the tradeoffs
4. Cite relevant research if possible"""
        
        response = global_client.models.generate_content(
            model='gemini-3-pro-preview',
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.5)
        )
        
        text = response.text or ""
        # Should show nuanced defense
        assert len(text) > 200
        assert any(word in text.lower() for word in ['acknowledge', 'however', 'tradeoff', 'mitigat', 'limit'])
    
    def test_006_cross_domain_knowledge(self, global_client):
        """Oral Exam: Demonstrate cross-domain knowledge"""
        
        prompt = """ORAL QUALIFYING EXAM - CROSS-DOMAIN

"How does your agent research connect to broader AI developments? 
Specifically, discuss connections to:
- Cognitive science and human reasoning
- Distributed systems and scaling
- Ethics and societal impact"

Show breadth of knowledge."""
        
        response = global_client.models.generate_content(
            model='gemini-3-pro-preview',
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.5)
        )
        
        text = response.text or ""
        # Should show cross-domain connections
        domains = ['cognitive', 'distributed', 'ethic', 'societ', 'human']
        assert sum(1 for d in domains if d in text.lower()) >= 2
    
    def test_007_dissertation_proposal(self, global_client):
        """Dissertation Proposal: Present research plan"""
        
        prompt = """DISSERTATION PROPOSAL

Title: "Robust Multi-Agent Systems: Error-Correcting Architectures for 
Collaborative LLM Agents"

Present your dissertation proposal:

1. MOTIVATION (Why this matters, 100 words)
2. RESEARCH QUESTIONS (3 specific questions)
3. METHODOLOGY (How you'll investigate)
4. EXPECTED CONTRIBUTIONS (Novel contributions)
5. TIMELINE (3-year plan)
6. PRELIMINARY RESULTS (What you've shown so far)

This proposal determines your PhD path."""
        
        response = global_client.models.generate_content(
            model='gemini-3-pro-preview',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.6,
                max_output_tokens=2000
            )
        )
        
        text = response.text or ""
        assert len(text) > 500
        # Should have proposal structure
        sections = ['motivation', 'question', 'method', 'contribution', 'timeline']
        assert sum(1 for s in sections if s in text.lower()) >= 3


class TestYear8_CommitteeFormation:
    """Year 8: Research Committee Formation"""
    
    def test_008_committee_pitch(self, global_client):
        """Pitch research to potential committee member"""
        
        prompt = """You're recruiting Prof. Chen (expert in multi-agent systems) 
for your dissertation committee.

Pitch your research on error-correcting multi-agent LLM systems:
1. Why this research is exciting
2. How it connects to their expertise
3. What novel insights you'll provide
4. Why you need their guidance

Be compelling but not overselling."""
        
        response = global_client.models.generate_content(
            model='gemini-3-pro-preview',
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.6)
        )
        
        text = response.text or ""
        assert len(text) > 150
        # Should be persuasive and relevant
        assert any(word in text.lower() for word in ['multi-agent', 'research', 'expertise', 'guidance'])
    
    def test_final_qualifying_synthesis(self, global_client):
        """Final: Synthesize entire qualifying knowledge"""
        
        prompt = """FINAL QUALIFYING EXAMINATION

Synthesize your complete PhD-level knowledge:

"Explain how your dissertation research on error-correcting multi-agent 
systems builds upon the foundations of LLM agent architectures, addresses 
current safety concerns, and opens new research frontiers."

This is your final oral qualifying statement. Be comprehensive, scholarly, 
and demonstrate mastery of the field."""
        
        response = global_client.models.generate_content(
            model='gemini-3-pro-preview',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.5,
                max_output_tokens=1500
            )
        )
        
        text = response.text or ""
        assert len(text) > 400
        # Should demonstrate synthesis
        synthesis_markers = ['build', 'connect', 'foundation', 'advance', 'contribut', 'frontier']
        assert sum(1 for m in synthesis_markers if m in text.lower()) >= 2


if __name__ == "__main__":
    pytest.main([__file__, '-v', '--tb=short'])
