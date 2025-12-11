"""Year 11: Publication & Defense Preparation Tests

PhD Year 5 — Pre-Defense Phase

Covers:
- Journal Publication
- Dissertation Writing  
- Defense Preparation
- Community Contribution

Required: Complete all milestones to proceed to defense
"""

import pytest
import os
import time
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
# JOURNAL PUBLICATION
# ============================================================================

class TestJournalPublication:
    """Journal Publication Phase"""
    
    def test_001_journal_selection(self, global_client):
        """Select appropriate journal and justify choice"""
        
        prompt = """JOURNAL SELECTION

Your research: Error-Correcting Multi-Agent LLM Systems

Evaluate 3 potential journals:
1. JMLR (Journal of Machine Learning Research)
2. TMLR (Transactions on Machine Learning Research) 
3. Artificial Intelligence Journal

For each:
- Impact factor / prestige
- Typical review time
- Fit with your work
- Likelihood of acceptance

Recommend one with justification."""
        
        response = global_client.models.generate_content(
            model='gemini-3-pro-preview',
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.5)
        )
        
        text = response.text or ""
        assert len(text) > 200
        # Should analyze journals
        assert any(j in text for j in ['JMLR', 'TMLR', 'Journal', 'Artificial Intelligence'])
    
    def test_002_extended_paper_writing(self, global_client):
        """Extend conference paper to journal version"""
        
        prompt = """JOURNAL EXTENSION

Your conference paper was 8 pages. The journal version needs 20+ pages.

What will you add?
1. Extended related work (what new papers?)
2. Additional experiments (what new conditions?)
3. Deeper analysis (what new insights?)
4. Appendix materials (proofs, implementation details?)

Outline the extended content specifically."""
        
        response = global_client.models.generate_content(
            model='gemini-3-pro-preview',
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.5)
        )
        
        text = response.text or ""
        assert len(text) > 300
        # Should outline extensions
        extensions = ['extend', 'add', 'additional', 'new', 'expand']
        assert sum(1 for e in extensions if e in text.lower()) >= 2


# ============================================================================
# DISSERTATION WRITING
# ============================================================================

class TestDissertationWriting:
    """Dissertation Writing Phase"""
    
    def test_003_dissertation_structure(self, global_client):
        """Design dissertation structure"""
        
        prompt = """DISSERTATION STRUCTURE

Design your PhD dissertation structure:

Title: "Robust Multi-Agent Systems: Error-Correcting Architectures for Collaborative LLM Agents"

Provide:
1. Complete chapter outline (8-10 chapters)
2. Estimated page count per chapter
3. Key figures/tables per chapter
4. Total dissertation length estimate

Follow CS dissertation conventions."""
        
        response = global_client.models.generate_content(
            model='gemini-3-pro-preview',
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.5)
        )
        
        text = response.text or ""
        assert len(text) > 300
        # Should have chapter structure
        assert 'chapter' in text.lower()
    
    def test_004_conclusion_writing(self, global_client):
        """Write dissertation conclusion"""
        
        prompt = """DISSERTATION CONCLUSION

Write the conclusion chapter (~500 words) for your dissertation:

Cover:
1. Summary of contributions (list 3-4 key contributions)
2. Limitations and scope
3. Future work directions (3 specific directions)
4. Broader impact on the field
5. Closing statement

Be confident but humble."""
        
        response = global_client.models.generate_content(
            model='gemini-3-pro-preview',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.5,
                max_output_tokens=1000
            )
        )
        
        text = response.text or ""
        word_count = len(text.split())
        assert word_count >= 250
        # Should summarize contributions
        assert any(word in text.lower() for word in ['contribut', 'future', 'limit', 'impact'])


# ============================================================================
# DEFENSE PREPARATION
# ============================================================================

class TestDefensePreparation:
    """Defense Preparation Phase"""
    
    def test_005_defense_presentation(self, global_client):
        """Create defense presentation outline"""
        
        prompt = """DEFENSE PRESENTATION

Create a 45-minute PhD defense presentation outline:

Structure with timing:
1. Introduction (5 min)
2. Background & Motivation (5 min)
3. Research Questions (3 min)
4. Methodology (7 min)
5. Results (15 min)
6. Discussion (5 min)
7. Conclusions & Future Work (5 min)

For each section:
- Key points to cover
- Slides needed
- Anticipated questions

Make it compelling and clear."""
        
        response = global_client.models.generate_content(
            model='gemini-3-pro-preview',
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.5)
        )
        
        text = response.text or ""
        assert len(text) > 400
        # Should have presentation structure
        assert any(word in text.lower() for word in ['slide', 'minute', 'present', 'section'])
    
    def test_006_tough_questions(self, global_client):
        """Prepare for tough committee questions"""
        
        prompt = """DEFENSE Q&A PREPARATION

Prepare answers for these tough committee questions:

Q1: "Why should we believe your results generalize beyond your test domains?"

Q2: "Your computational overhead is 30% higher. Is this acceptable for real-world deployment?"

Q3: "What if your error detection itself has errors? Doesn't this create an infinite regress?"

Q4: "How does your work differ substantially from [Competing Approach]?"

Provide thoughtful, honest answers for each."""
        
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
        # Should address questions
        assert 'Q' in text or 'question' in text.lower() or len(text.split('\n')) > 5
    
    def test_007_practice_defense(self, global_client):
        """Simulate practice defense"""
        
        prompt = """PRACTICE DEFENSE SIMULATION

You're giving your 2-minute elevator pitch for your dissertation:

"My dissertation is about..."

Complete this in exactly 2 minutes of spoken word (~300 words).
Cover:
- What problem you solved
- How you solved it
- Why it matters
- Key results

Make it accessible to a general technical audience."""
        
        response = global_client.models.generate_content(
            model='gemini-3-pro-preview',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.6,
                max_output_tokens=500
            )
        )
        
        text = response.text or ""
        word_count = len(text.split())
        assert word_count >= 150
    
    def test_final_defense_ready(self, global_client):
        """Final: Assess defense readiness"""
        
        prompt = """YEAR 11 FINAL: DEFENSE READINESS ASSESSMENT

Evaluate your readiness to defend:

1. DISSERTATION COMPLETE: Is the writing finished? [Yes/No]
2. PUBLICATIONS: How many papers published/submitted?
3. PRESENTATIONS: How many practice talks given?
4. COMMITTEE STATUS: All members confirmed?
5. CONFIDENCE LEVEL: Rate 1-10 your readiness

Then answer: "Are you ready to schedule your defense?"

Be honest about any remaining gaps."""
        
        response = global_client.models.generate_content(
            model='gemini-3-pro-preview',
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.5)
        )
        
        text = response.text or ""
        assert len(text) > 200
        # Should assess readiness
        assert any(word in text.lower() for word in ['ready', 'complete', 'yes', 'no', 'confiden'])


if __name__ == "__main__":
    pytest.main([__file__, '-v', '--tb=short'])
