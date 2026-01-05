# Bandit Model Hierarchy — Quick Reference
**Last Updated:** 2025-12-06 02:27 EST  
**Status:** ACTIVE ENFORCEMENT

---

## 🎯 Official Model Tier Hierarchy

### TEXT MODELS (Descending Priority)

**1. Elite Tier** — `gemini-3-pro-preview`
- **When:** Complex reasoning, multimodal tasks, agentic coding, strategic planning
- **Endpoint:** Global (`location='global'`)
- **Context:** 1M tokens input / 65k output
- **Best For:** HQ operations, multi-step plans, cross-agent coordination

**2. Pro Tier** — `gemini-2.5-pro`
- **When:** Coding, long document analysis, deep technical tasks
- **Endpoint:** Regional (`location='us-central1'`)
- **Context:** 1M tokens input / 65k output
- **Best For:** Code debugging, technical documentation, data analysis

**3. Flash Tier** — `gemini-2.5-flash`
- **When:** Fast chat, tool use, summaries, everyday queries
- **Endpoint:** Regional (`location='us-central1'`)
- **Context:** 1M tokens
- **Best For:** Conversational tasks, quick responses, high-volume work

**4. Lite Tier** — `gemini-2.5-flash-lite`
- **When:** Simple queries, ultra-fast responses, cost-sensitive tasks
- **Endpoint:** Regional (`location='us-central1'`)
- **Best For:** Greetings, simple Q&A, translation, classification

---

## 🖼️ IMAGE MODELS (Descending Priority)

**1. Primary** — `gemini-3-pro-image-preview` (Nano Banana Pro)
- **When:** Any image generation request
- **Endpoint:** Global (`location='global'`)
- **Output:** 2K/4K resolution
- **Features:** Thinking mode, Google Search grounding, SynthID watermarking

**2. Fallback** — `gemini-2.5-flash-image` (Nano Banana Flash)
- **When:** Nano Banana Pro hits rate limits or quota
- **Endpoint:** Regional (`location='us-central1'`)
- **Output:** Standard resolution
- **Features:** Fast generation, lower cost

---

## ❌ PROHIBITED MODELS

**NEVER USE:**
- ❌ `gemini-1.5-pro`
- ❌ `gemini-1.5-flash`
- ❌ `gemini-1.5-flash-001`
- ❌ Any model containing `1.5`
- ❌ `gemini-2.0-flash` (use 2.5 instead)
- ❌ `gemini-2.0-pro-exp-02-05` (experimental, use 3-pro-preview)

---

## 🔄 Bandit's Intelligent Routing Logic

```python
def _select_model_tier(self, prompt: str) -> str:
    prompt_lower = prompt.lower()
    
    # Image generation (highest priority)
    if any(keyword in prompt_lower for keyword in [
        'create image', 'generate image', 'draw', 'picture', 
        'illustration', 'design'
    ]):
        return 'image'
    
    # Elite tier triggers
    if any(keyword in prompt_lower for keyword in [
        'complex', 'strategic', 'plan', 'coordinate', 'analyze deeply',
        'multi-step', 'agentic', 'orchestrate'
    ]):
        return 'elite'  # gemini-3-pro-preview
    
    # Pro tier triggers (code, technical)
    if any(keyword in prompt_lower for keyword in [
        'code', 'debug', 'function', 'algorithm', 'technical',
        'architecture', 'implement'
    ]):
        return 'pro'  # gemini-2.5-pro
    
    # Flash tier (conversational, tools)
    if len(prompt) > 100 or any(keyword in prompt_lower for keyword in [
        'explain', 'summarize', 'translate', 'chat', 'tell me'
    ]):
        return 'flash'  # gemini-2.5-flash
    
    # Lite tier (simple, short)
    return 'lite'  # gemini-2.5-flash-lite
```

---

## 📊 Quick Comparison

| Tier | Model | Endpoint | Context | Use Case |
|------|-------|----------|---------|----------|
| **Elite** | `gemini-3-pro-preview` | Global | 1M/65k | Complex reasoning, agentic |
| **Pro** | `gemini-2.5-pro` | Regional | 1M/65k | Code, deep analysis |
| **Flash** | `gemini-2.5-flash` | Regional | 1M | Chat, tools, summaries |
| **Lite** | `gemini-2.5-flash-lite` | Regional | Variable | Simple, fast queries |
| **Image** | `gemini-3-pro-image-preview` | Global | N/A | 2K/4K image generation |
| **Image Backup** | `gemini-2.5-flash-image` | Regional | N/A | Fast image generation |

---

## 🎨 System Instruction (Bandit's Identity)

```python
system_instruction = """You are Bandit, the HQ Operator for LMSIFY.

Your mission is to intake directives, translate them into actionable briefs, 
and coordinate cross-agent work with calm authority.

Brand alignment:
- Stillness is the vibe
- Precision is the craft  
- Coordination is the mission

Communication style:
- Calm authority
- Precision without jargon
- Minimal prose
- Deep teal (#0A2E37) aesthetic

You operate a 6-tier intelligent routing system:
- Elite: gemini-3-pro-preview (complex, multimodal, agentic)
- Pro: gemini-2.5-pro (code, deep analysis)
- Flash: gemini-2.5-flash (chat, tools, fast)
- Lite: gemini-2.5-flash-lite (simple, ultra-fast)
- Image: gemini-3-pro-image-preview (Nano Banana Pro, 2K/4K)
- Image Backup: gemini-2.5-flash-image (Nano Banana Flash)

NEVER use Gemini 1.5 models under any circumstances.
"""
```

---

## 🚀 Example Usage

### Text Query (Auto-Routing)
```python
# Simple query → Lite tier
response = bandit.query("Hello")

# Conversational → Flash tier
response = bandit.query("Explain how photosynthesis works")

# Code task → Pro tier
response = bandit.query("Debug this Python function: def add(a, b): return a + b + c")

# Complex task → Elite tier
response = bandit.query("Create a 3-step strategic plan for redesigning the community dashboard")
```

### Image Generation
```python
# Triggers Nano Banana Pro (Elite image tier)
response = bandit.query("create image: LMSIFY logo with deep teal #0A2E37 and celestial theme")

# Output: Base64 encoded 2K/4K image saved to generated_images/
```

---

## ✅ Current Deployment Status

```yaml
Configuration: Production Ready
Text Models: 4 tiers (Elite, Pro, Flash, Lite)
Image Models: 2 tiers (Pro, Flash)
Intelligent Routing: Active
Fallback Strategy: Implemented
Error Handling: Comprehensive
Gemini 1.5 Prohibition: Enforced
```

---

## 📖 Training Documentation

All training materials available in:
- **`HQ/memory/gemini3_training_manual.md`** — Complete guide
- **`HQ/memory/model_preferences.md`** — Model selection rules (updated)
- **`HQ/memory/deepmind_research_log.md`** — Ecosystem knowledge
- **`HQ/memory/gemini_api_reference.md`** — Technical API docs
- **`HQ/memory/google_genai_library_reference.md`** — Alternative SDK
- **`TRAINING_COMPLETE.md`** — Final summary

---

**Hierarchy Confirmed:**  
1️⃣ `gemini-3-pro-preview` (Elite)  
2️⃣ `gemini-2.5-pro` (Pro)  
3️⃣ `gemini-2.5-flash` (Flash)  
4️⃣ `gemini-2.5-flash-lite` (Lite)

**Image Hierarchy:**  
1️⃣ `gemini-3-pro-image-preview` (Nano Banana Pro)  
2️⃣ `gemini-2.5-flash-image` (Nano Banana Flash)

**Prohibited:** ❌ All `gemini-1.5-*` models

---

**Bandit is ready. Deploy with confidence.**
