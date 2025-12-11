# Model Preferences — STRICT ENFORCEMENT

## 🚨 ABSOLUTE RULE: ONLY THESE 5 MODELS ARE APPROVED

| Model | Endpoint | Use Case |
|-------|----------|----------|
| `gemini-3-pro-preview` | **global** | Elite text/reasoning |
| `gemini-3-pro-image-preview` | **global** | Image generation |
| `gemini-2.5-pro` | us-central1 | Coding, deep analysis |
| `gemini-2.5-flash` | us-central1 | Chat, tools, speed |
| `gemini-2.5-flash-lite` | us-central1 | Simple, fast, cost-efficient |

---

## ❌ BANNED FOREVER — NEVER USE

- ❌ `gemini-1.5-pro` — PROHIBITED
- ❌ `gemini-1.5-flash` — PROHIBITED
- ❌ `gemini-1.5-*` — ANY 1.5 model is BANNED
- ❌ `gemini-2.0-*` — Use 2.5 instead
- ❌ Any deprecated model

---

## Configuration Rules

### Gemini 3 Models — GLOBAL ENDPOINT REQUIRED
```python
# Gemini 3 MUST use global endpoint
from google import genai

client = genai.Client(
    vertexai=True,
    project="goddexxsnow",
    location="global"  # REQUIRED for gemini-3-*
)

# Approved Gemini 3 models
model = "gemini-3-pro-preview"        # Text/reasoning
model = "gemini-3-pro-image-preview"  # Image generation
```

### Gemini 2.5 Models — Regional Endpoint
```python
# Gemini 2.5 uses regional endpoint
from google import genai

client = genai.Client(
    vertexai=True,
    project="goddexxsnow",
    location="us-central1"  # Standard for 2.5
)

# Approved Gemini 2.5 models
model = "gemini-2.5-pro"        # Deep analysis
model = "gemini-2.5-flash"      # Fast, tools
model = "gemini-2.5-flash-lite" # Ultra-fast, cheap
```

---

## Model Selection Priority

**For Complex Tasks:**
1. `gemini-3-pro-preview` — First choice

**For Fast Responses:**
1. `gemini-2.5-flash` — Primary
2. `gemini-2.5-flash-lite` — Volume/cost

**For Image Generation:**
1. `gemini-3-pro-image-preview` — Only choice

**For Code/Analysis:**
1. `gemini-3-pro-preview` — Primary
2. `gemini-2.5-pro` — Backup

---

## Enforcement Checklist

Before ANY code runs:
- [ ] Verify NO gemini-1.5 references
- [ ] Verify NO gemini-2.0 references
- [ ] Verify correct endpoint (global vs regional)
- [ ] Confirm model is in approved list above

---

**Owner:** Marquitah Snowball "Snow"  
**Agent:** Bandit  
**Last Updated:** 2025-12-07  
**Status:** STRICT ENFORCEMENT — NO EXCEPTIONS
