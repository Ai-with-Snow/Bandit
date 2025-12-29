# Gemini Model Reference for Bandit

> **Default Model: `gemini-3-flash-preview`**
> All models have **1M token context window** and **64K output**

---

## Model Tiers

| Mode | Model | Use Case |
|------|-------|----------|
| **Instant** | `gemini-3-flash-preview` | Fast responses, low latency |
| **Auto** | `gemini-3-flash-preview` | Balanced (handles most tasks) |
| **Thinking** | `gemini-3-pro-preview` | Deep reasoning, complex tasks |

---

## Gemini 3 Models

| Model String | Context | Pricing (per 1M tokens) | Free Tier |
|--------------|---------|-------------------------|-----------|
| `gemini-3-flash-preview` | 1M in / 64K out | In: $0.50 / Out: $3.00 | ✅ Yes |
| `gemini-3-pro-preview` | 1M in / 64K out | In: $2-4 / Out: $12-18 | ❌ No |
| `gemini-3-pro-image-preview` | 64K in / 32K out | In: $2 / Out: $12 + per image | ❌ No |

---

## Gemini 2.5 Models

| Model String | Context | Pricing (per 1M tokens) | Free Tier |
|--------------|---------|-------------------------|-----------|
| `gemini-2.5-pro` | 1M in / 64K out | In: $1.25-2.50 / Out: $10-15 | ✅ Yes |
| `gemini-2.5-flash` | 1M in / 64K out | In: $0.30 / Out: $2.50 | ✅ Yes |
| `gemini-2.5-flash-lite` | 1M in / 64K out | In: $0.10 / Out: $0.40 | ✅ Yes |

---

## Bandit Configuration

### CLI (`scripts/bandit_cli.py`)
```python
SEARCH_MODEL = "gemini-3-flash-preview"
RAG_MODEL = "gemini-3-flash-preview"
DEFAULT_MODEL = "gemini-3-flash-preview"
```

### Proxy (`proxy_server.py`)
```python
FAST_MODEL = "gemini-3-flash-preview"      # Instant mode
FULL_MODEL = "gemini-3-flash-preview"      # Auto mode
DEEP_THINK_MODEL = "gemini-3-pro-preview"  # Deep think
```

### Agents (`scripts/agents.py`)
```python
DEFAULT_MODEL = "gemini-3-flash-preview"
```

---

## Capabilities

All Gemini 3 models support:
- ✅ Text
- ✅ Images
- ✅ Video
- ✅ Audio
- ✅ PDF
- ✅ Code execution
- ✅ Google Search grounding
- ✅ URL context analysis
- ✅ Function calling

---

## API Endpoints

| Endpoint | Tool |
|----------|------|
| `/chat` | General chat |
| `/search` | Google Search grounding |
| `/analyze-url` | URL context analysis |
| `/execute-code` | Python code execution |
| `/research` | Deep research (async) |
| `/v1/embeddings` | Text embeddings |

---

## Rate Limits (Tier 1)

| Model | Enqueued Tokens |
|-------|-----------------|
| gemini-3-pro-preview | 5M |
| gemini-3-flash-preview | 3M |
| gemini-2.5-flash-lite | 10M |

---

## Text-to-Speech (TTS) Models

| Model String | Type | Speakers | Context | Features |
|--------------|------|----------|---------|----------|
| `gemini-2.5-pro-preview-tts` | High Control | Multi | 8K/16K | Best quality, podcasts |
| `gemini-2.5-flash-preview-tts` | Fast | Multi | 8K/16K | Low latency, cost-efficient |
| `gemini-2.5-flash-lite-preview-tts` | Ultra-Fast | Single | 8K/16K | Lowest latency |

### TTS Voices (30 Available)

**Female Voices:**
- Zephyr (Bright), Kore (Firm), Leda (Youthful), Aoede (Breezy)
- Callirrhoe (Easy-going), Autonoe (Bright), Erinome (Clear)
- Laomedeia (Upbeat), Pulcherrima (Forward), Vindemiatrix (Gentle)
- Achernar (Soft), Despina (Smooth), Gacrux (Mature), Sulafat (Warm)

**Male Voices:**
- Puck (Upbeat), Charon (Informative), Fenrir (Excitable), Orus (Firm)
- Enceladus (Breathy), Iapetus (Clear), Umbriel (Easy-going)
- Algieba (Smooth), Algenib (Gravelly), Rasalgethi (Informative)
- Alnilam (Firm), Schedar (Even), Achird (Friendly)
- Zubenelgenubi (Casual), Sadachbia (Lively), Sadaltager (Knowledgeable)

### TTS Control Features
- **Natural Language Prompts** — Control style, accent, pace, tone, emotion
- **Markup Tags** — `[sigh]`, `[whisper]`, `[laugh]` for specific actions
- **Multi-speaker** — Up to 2 speakers with distinct voices
- **Streaming** — Real-time audio generation

### TTS Pricing
| Model | Input (per 1M) | Output (Audio) |
|-------|----------------|----------------|
| Pro TTS | $1.00 | $20.00 |
| Flash TTS | $0.50 | $10.00 |

---

*Last Updated: December 28, 2025*
