# Gemini API Quick Reference Cheat Sheet

> **One-page essential reference** for rapid development  
> **Updated**: December 6, 2025  
> **Full Documentation**: See `gemini_api_master_index.md`

---

## 🚀 Quick Start (5 Minutes)

```python
# Install SDK
pip install -U google-genai

# Set API key (get from aistudio.google.com/api-keys)
export GEMINI_API_KEY="your-api-key"

# Generate text
from google import genai
client = genai.Client()
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='Explain quantum computing in 3 sentences'
)
print(response.text)
```

---

## 🎯 Model Selection Guide

```
┌─────────────────────────────────────────────────────────────┐
│ USE CASE                    │ RECOMMENDED MODEL            │
├─────────────────────────────┼──────────────────────────────┤
│ Complex reasoning/agents    │ gemini-3-pro-preview         │
│ Long context (1M+ tokens)   │ gemini-2.5-pro               │
│ General-purpose, fast       │ gemini-2.5-flash (BEST)      │
│ High-volume, low-cost       │ gemini-2.5-flash-lite        │
│ Image generation            │ gemini-2.5-flash-image       │
│ Video generation            │ veo-3.1-generate-001         │
│ Real-time voice/video       │ gemini-2.5-flash-native-audio│
│ Embeddings                  │ gemini-embedding-001         │
└─────────────────────────────────────────────────────────────┘
```

---

## 📝 Core API Patterns

### **Generate Content**
```python
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='Your prompt here'
)
print(response.text)
```

### **Streaming**
```python
for chunk in client.models.generate_content_stream(
    model='gemini-2.5-flash',
    contents='Tell me a story'
):
    print(chunk.text, end='')
```

### **Multimodal (Image + Text)**
```python
from PIL import Image

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=[
        'Describe this image in detail',
        Image.open('photo.jpg')
    ]
)
```

### **Chat**
```python
chat = client.chats.create(model='gemini-2.5-flash')
response1 = chat.send_message(message='What is AI?')
response2 = chat.send_message(message='Give me an example')
```

### **Structured Output (JSON)**
```python
from pydantic import BaseModel

class Recipe(BaseModel):
    name: str
    ingredients: list[str]
    steps: list[str]

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='Give me a cookie recipe',
    config={
        'response_mime_type': 'application/json',
        'response_schema': Recipe
    }
)
print(response.parsed)  # Automatically parsed to Recipe object
```

---

## 🛠️ Essential Tools

### **Google Search Grounding**
```python
from google.genai import types

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='What is the Google stock price today?',
    config=types.GenerateContentConfig(
        tools=[types.Tool(google_search=types.GoogleSearch())]
    )
)
```

### **Code Execution**
```python
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='Calculate the sum of first 50 prime numbers',
    config=types.GenerateContentConfig(
        tools=[types.Tool(code_execution=types.ToolCodeExecution)]
    )
)
```

### **Function Calling (Automatic)**
```python
def get_weather(location: str) -> str:
    """Get current weather for a location.
    
    Args:
        location: City name, e.g., 'San Francisco'
    """
    return "23°C and sunny"

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='What is the weather in Boston?',
    config=types.GenerateContentConfig(tools=[get_weather])
)
# Function is automatically called and result included in response
```

---

## ⚡ Production Optimizations

### **Context Caching (50% cost savings)**
```python
# Upload file
document = client.files.upload(file='large_document.pdf')

# Create cache
cache = client.caches.create(
    model='gemini-2.5-flash',
    config={'contents': [document]}
)

# Use cached content (reuse for multiple queries)
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='Summarize page 10',
    config=types.GenerateContentConfig(cached_content=cache.name)
)
```

### **Batch API (50% discount, async processing)**
```python
# Create batch request
batch = client.batches.create(requests=[
    {'model': 'gemini-2.5-flash', 'contents': 'Query 1'},
    {'model': 'gemini-2.5-flash', 'contents': 'Query 2'},
    # ... up to 10,000 requests
])

# Poll for completion
while batch.state == 'PROCESSING':
    time.sleep(10)
    batch = client.batches.get(name=batch.name)

# Get results
for result in batch.results:
    print(result.response.text)
```

---

## 🎨 Configuration Options

```python
from google.genai import types

config = types.GenerateContentConfig(
    # System instructions
    system_instruction='You are a helpful assistant',
    
    # Generation parameters
    temperature=1.0,           # 0.0-2.0 (keep at 1.0 for Gemini 3)
    top_p=0.95,                # Nucleus sampling
    top_k=40,                  # Top-k sampling
    max_output_tokens=8192,    # Response length limit
    
    # Safety settings
    safety_settings=[
        types.SafetySetting(
            category='HARM_CATEGORY_HATE_SPEECH',
            threshold='BLOCK_ONLY_HIGH'
        )
    ],
    
    # Thinking (for reasoning tasks)
    thinking_config=types.ThinkingConfig(
        thinking_budget='balanced'  # 'fast' | 'balanced' | 'deep'
    ),
    
    # Response format
    response_mime_type='application/json',
    response_schema=YourPydanticClass,
    
    # Stop sequences
    stop_sequences=['\n\n', 'END'],
    
    # Seed for reproducibility
    seed=42
)

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='Your prompt',
    config=config
)
```

---

## 🔐 Authentication

### **API Key (Simplest)**
```bash
export GEMINI_API_KEY="your-api-key"
```

```python
from google import genai
client = genai.Client()  # Auto-detects GEMINI_API_KEY
```

### **Vertex AI (Enterprise)**
```python
client = genai.Client(
    vertexai=True,
    project='your-project-id',
    location='us-central1'
)
```

---

## 💰 Cost Optimization

| **Strategy** | **Savings** | **Implementation** |
|--------------|-------------|-------------------|
| Use Flash-Lite | 80% cheaper than Pro | Switch model for simple tasks |
| Context Caching | 50% for cached tokens | Cache large docs/context |
| Batch API | 50% discount | Use for non-urgent tasks |
| Media Resolution | Reduce token usage | Set `image_resolution='low'` |
| Thinking Budget | Balance cost/quality | Set `thinking_budget='fast'` |

---

## 🚨 Common Issues & Fixes

| **Error** | **Cause** | **Solution** |
|-----------|-----------|--------------|
| 400 INVALID_ARGUMENT | Malformed request | Check API reference for format |
| 403 PERMISSION_DENIED | Wrong API key | Verify key from AI Studio |
| 404 NOT_FOUND | Resource not found | Check model name/file URI |
| 429 RESOURCE_EXHAUSTED | Rate limit hit | Slow down or upgrade to paid |
| 500 INTERNAL | Server error | Retry or switch model |
| 503 UNAVAILABLE | Service overloaded | Wait and retry |

### **Repetitive Output?**
- Keep `temperature=1.0` (especially for Gemini 3)
- Add "Be concise, don't repeat" to prompt
- Avoid explicit thinking instructions

### **Safety Blocks?**
- Review prompt against Prohibited Use Policy
- Adjust safety settings if appropriate
- `BlockedReason.OTHER` = Terms of Service violation

---

## 📊 Token & Context Limits

| **Model** | **Input Tokens** | **Output Tokens** | **Context Window** |
|-----------|------------------|-------------------|--------------------|
| Gemini 3 Pro | 1M | 8,192 | 1M |
| Gemini 2.5 Pro | 2M | 8,192 | 2M |
| Gemini 2.5 Flash | 1M | 8,192 | 1M |
| Gemini 2.5 Flash-Lite | 1M | 8,192 | 1M |

```python
# Count tokens
response = client.models.count_tokens(
    model='gemini-2.5-flash',
    contents='Your prompt here'
)
print(response.total_tokens)
```

---

## 🌍 Important Links

- **AI Studio**: https://aistudio.google.com
- **API Keys**: https://aistudio.google.com/api-keys
- **Documentation**: https://ai.google.dev/gemini-api/docs
- **Pricing**: https://ai.google.dev/pricing
- **Rate Limits**: https://ai.google.dev/gemini-api/docs/rate-limits
- **Python SDK**: https://github.com/googleapis/python-genai
- **Developer Forum**: https://discuss.ai.google.dev

---

## 🎓 Best Practices

### **Prompting**
- Be specific and clear
- Use few-shot examples
- Structure with headings/bullets
- Include output format requirements
- Use system instructions for persona/constraints

### **Production**
- Enable logging for debugging
- Configure safety settings appropriately
- Use streaming for better UX
- Implement retry logic with exponential backoff
- Monitor token usage and costs

### **Security**
- Never hardcode API keys
- Use environment variables
- Rotate keys regularly
- Enable Cloud Billing for production
- Don't submit sensitive data to free tier

---

## 📚 Advanced Features

### **Live API (Real-time voice/video)**
```python
session = client.live.connect(model='gemini-2.5-flash-native-audio')
# Bidirectional streaming for voice/video
```

### **File Search RAG**
```python
corpus = client.corpora.create(display_name='My Docs')
# Upload docs, create index, query with grounding
```

### **Computer Use (UI Automation)**
```python
# Gemini 2.5 Computer Use can control UI
response = client.models.generate_content(
    model='gemini-2.5-computer-use-preview',
    contents='Click the submit button'
)
```

---

## ⚖️ Compliance

- **Age Requirement**: 18+
- **Available Regions**: 150+ countries (see docs)
- **Terms**: ai.google.dev/gemini-api/terms
- **Prohibited Uses**: No hate speech, harassment, illegal activities
- **Data Usage**:
  - **Free tier**: Used to improve Google products
  - **Paid tier**: Not used to train models (with Cloud Billing)

---

**Stillness is the vibe.** 🎯

*For complete documentation, see `gemini_api_master_index.md`*
