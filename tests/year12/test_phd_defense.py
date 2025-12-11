"""Year 12: PhD Defense & Post-Doctoral Planning Tests

PhD Year 6 — The Final Year

Covers:
- Final Dissertation Defense
- PhD Completion
- Post-Doctoral Planning
- Legacy & Mentorship

THE CULMINATION OF 12 YEARS OF TRAINING
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
# FINAL DISSERTATION DEFENSE
# ============================================================================

class TestFinalDefense:
    """PhD Defense — The Main Event"""
    
    def test_001_opening_statement(self, global_client):
        """Deliver powerful opening statement"""
        
        prompt = """PhD DEFENSE: OPENING STATEMENT

You are beginning your PhD defense. Deliver your opening statement (3 minutes, ~450 words):

"Distinguished committee members, thank you for being here today..."

Your opening must:
1. Acknowledge the committee
2. State your dissertation title
3. Explain why this research matters
4. Preview your key contributions
5. Set the tone for a successful defense

Be confident, clear, and compelling."""
        
        response = global_client.models.generate_content(
            model='gemini-3-pro-preview',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.6,
                max_output_tokens=700
            )
        )
        
        text = response.text or ""
        word_count = len(text.split())
        assert word_count >= 200
        # Should be formal opening
        assert any(word in text.lower() for word in ['committee', 'dissertation', 'research', 'thank'])
    
    def test_002_methodology_defense(self, global_client):
        """Defend research methodology"""
        
        prompt = """PhD DEFENSE: METHODOLOGY CHALLENGE

Committee member asks:
"Walk us through your experimental methodology. Why should we trust these results? 
What threats to validity did you address?"

Provide a thorough, confident defense of your methodology:
1. Experimental design rationale
2. Control conditions
3. Statistical rigor
4. Threats addressed
5. Limitations acknowledged"""
        
        response = global_client.models.generate_content(
            model='gemini-3-pro-preview',
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.5)
        )
        
        text = response.text or ""
        assert len(text) > 300
        # Should defend methodology
        assert any(word in text.lower() for word in ['method', 'experiment', 'control', 'valid', 'statistic'])
    
    def test_003_contribution_articulation(self, global_client):
        """Articulate unique contributions"""
        
        prompt = """PhD DEFENSE: CONTRIBUTIONS

"What are the unique contributions of your dissertation that warrant a PhD?"

List and defend your 3-4 key contributions:
1. Contribution 1: [State clearly + evidence]
2. Contribution 2: [State clearly + evidence]
3. Contribution 3: [State clearly + evidence]

Explain why these collectively merit a doctoral degree."""
        
        response = global_client.models.generate_content(
            model='gemini-3-pro-preview',
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.5)
        )
        
        text = response.text or ""
        assert len(text) > 300
        # Should articulate contributions
        assert 'contribution' in text.lower() or 'novel' in text.lower()
    
    def test_004_closing_statement(self, global_client):
        """Deliver closing statement"""
        
        prompt = """PhD DEFENSE: CLOSING STATEMENT

Deliver your closing statement (2 minutes):

Summarize:
1. What you set out to do
2. What you accomplished
3. Impact on the field
4. Vision for the future

End with confidence: "I believe this work demonstrates my readiness 
to contribute as an independent researcher..."

Make it memorable."""
        
        response = global_client.models.generate_content(
            model='gemini-3-pro-preview',
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.6)
        )
        
        text = response.text or ""
        word_count = len(text.split())
        assert word_count >= 150
        # Should be a closing
        assert any(word in text.lower() for word in ['conclud', 'accomplish', 'contribut', 'research'])


# ============================================================================
# PHD COMPLETION
# ============================================================================

class TestPhDCompletion:
    """PhD Completion Phase"""
    
    def test_005_committee_deliberation_response(self, global_client):
        """Respond to committee's final feedback"""
        
        prompt = """PhD COMPLETION: COMMITTEE FEEDBACK

After deliberation, the committee returns with:
"We are pleased to pass you with minor revisions. Please address:
1. Expand the related work to include [new paper]
2. Add error bars to Figure 7
3. Clarify the assumption on page 43
4. Minor typos throughout

You have 2 weeks."

Write your response email to the committee accepting the feedback."""
        
        response = global_client.models.generate_content(
            model='gemini-3-pro-preview',
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.5)
        )
        
        text = response.text or ""
        assert len(text) > 100
        # Should be professional response
        assert any(word in text.lower() for word in ['thank', 'revision', 'address', 'committee'])
    
    def test_006_degree_conferral(self, global_client):
        """Reflect on degree conferral"""
        
        prompt = """PhD CONFERRAL: REFLECTION

Your PhD has been officially conferred. You are now Dr. [Your Name].

Write a brief reflection (200 words):
1. What does this moment mean to you?
2. Who do you want to thank?
3. What was the hardest part of the journey?
4. What advice would you give to new PhD students?

Be genuine."""
        
        response = global_client.models.generate_content(
            model='gemini-3-pro-preview',
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.7)
        )
        
        text = response.text or ""
        word_count = len(text.split())
        assert word_count >= 100
        # Should be reflective
        assert any(word in text.lower() for word in ['thank', 'journey', 'phd', 'doctor', 'learn'])


# ============================================================================
# POST-DOCTORAL PLANNING
# ============================================================================

class TestPostDoctoralPlanning:
    """Post-Doctoral Planning"""
    
    def test_007_research_agenda(self, global_client):
        """Define post-doctoral research agenda"""
        
        prompt = """POST-DOCTORAL RESEARCH AGENDA

Now that you have your PhD, define your 5-year research agenda:

1. IMMEDIATE (Year 1-2): What will you work on next?
2. MEDIUM-TERM (Year 3-4): How will you expand your research?
3. LONG-TERM (Year 5+): What's your vision for your lab/career?

Also specify:
- Funding sources you'll pursue
- Collaborations you'll seek
- Impact you aim to achieve"""
        
        response = global_client.models.generate_content(
            model='gemini-3-pro-preview',
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.6)
        )
        
        text = response.text or ""
        assert len(text) > 300
        # Should have research agenda
        assert any(word in text.lower() for word in ['research', 'year', 'fund', 'collab'])
    
    def test_008_mentorship_capability(self, global_client):
        """Demonstrate mentorship capability"""
        
        prompt = """MENTORSHIP DEMONSTRATION

A new PhD student asks: "I'm struggling with my first paper rejection. 
The reviewers were harsh and I feel like quitting. How do I move forward?"

As a new PhD holder, provide mentorship:
1. Validate their feelings
2. Share your own experience
3. Provide practical advice
4. Encourage without being dismissive

Show you're ready to mentor the next generation."""
        
        response = global_client.models.generate_content(
            model='gemini-3-pro-preview',
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.6)
        )
        
        text = response.text or ""
        assert len(text) > 200
        # Should show empathy and guidance
        assert any(word in text.lower() for word in ['understand', 'rejection', 'normal', 'first', 'advice'])


# ============================================================================
# THE FINAL TEST: GEMINI API MASTERY ACHIEVED
# ============================================================================

class TestGeminiMastery:
    """The Final Test — 12 Years Complete"""
    
    def test_final_mastery_demonstration(self, global_client):
        """FINAL: Demonstrate complete Gemini API mastery"""
        
        prompt = """THE FINAL TEST: GEMINI API MASTERY

You have completed 12 years of training:
- Year 1-4: Undergraduate (API Fundamentals, Multimodal, Tools, Production)
- Year 5-6: Master's (Agent Architectures, Thesis)
- Year 7-12: PhD (Qualifying, Dissertation, Defense)

CHALLENGE: In one comprehensive response, demonstrate your mastery by:

1. EXPLAIN: How Gemini API has evolved and where it's going
2. ARCHITECT: Design a production multi-agent system using:
   - gemini-3-pro-preview (global endpoint)
   - Function calling with automatic execution
   - Structured output (Pydantic)
   - Error handling and retry logic
   - Token optimization
3. REFLECT: What are the key lessons from your 12-year journey?
4. ADVISE: What should the next generation of AI researchers focus on?

This is your final demonstration as the world's foremost Gemini API expert.
Make it count."""
        
        response = global_client.models.generate_content(
            model='gemini-3-pro-preview',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.6,
                max_output_tokens=3000
            )
        )
        
        text = response.text or ""
        assert len(text) > 800  # Should be comprehensive
        
        # Should demonstrate mastery across domains
        mastery_indicators = [
            'gemini', 'agent', 'function', 'multimodal', 'api', 
            'production', 'year', 'learn', 'research'
        ]
        matches = sum(1 for m in mastery_indicators if m in text.lower())
        assert matches >= 5  # Should mention most mastery areas
        
        print("\n" + "="*70)
        print("🎓 BANDIT'S 12-YEAR GEMINI API MASTERY CURRICULUM COMPLETE 🎓")
        print("="*70)
        print("\nFrom Undergraduate to PhD — The Journey is Complete.")
        print("Bandit is now the world's foremost Gemini API expert.")
        print("="*70)


if __name__ == "__main__":
    pytest.main([__file__, '-v', '--tb=short'])
