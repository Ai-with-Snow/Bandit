# Google GenAI Library Reference
**Alternative SDK:** `google.genai` client library  
**Last Updated:** 2025-12-06 02:23 EST

---

## Overview

The `google.genai` library is an alternative to `vertexai` for accessing Gemini models. It provides a simpler, more Pythonic interface for common tasks.

**vs. Vertex AI SDK:**
- **google.genai:** Simpler API, auto-handles many details, great for prototyping
- **vertexai:** Full control, enterprise features, better for production deployments

**Bandit's Choice:** Currently uses `vertexai` for Reasoning Engine deployment, but `google.genai` is valuable for testing and future enhancements.

---

## Installation

```bash
pip install google-generativeai
# or
pip install google-genai
```

---

## Basic Setup

```python
from google import genai

# Initialize client
client = genai.Client()

# Simple text generation
response = client.models.generate_content(
    model="gemini-3-pro-preview",  # ✅ Use Gemini 3
    contents="Explain quantum physics"
)
print(response.text)
```

---

## ❌ CRITICAL: Model Selection

**ONLY USE GEMINI 2.5 OR GEMINI 3:**

```python
# ✅ CORRECT
model="gemini-3-pro-preview"
model="gemini-2.5-pro"
model="gemini-2.5-flash"
model="gemini-2.5-flash-lite"

# ❌ WRONG - NEVER USE GEMINI 1.5
model="gemini-1.5-flash"    # PROHIBITED
model="gemini-1.5-pro"      # PROHIBITED
```

---

## Text Generation

### Simple Text Query

```python
from google import genai

client = genai.Client()
response = client.models.generate_content(
    model="gemini-3-pro-preview",
    contents="Write a story about a magic backpack."
)
print(response.text)
```

### With Generation Config

```python
response = client.models.generate_content(
    model="gemini-3-pro-preview",
    contents="Write a poem",
    config={
        "temperature": 1.0,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192
    }
)
```

---

## Multimodal Input

### Image Understanding

```python
from google import genai
import PIL.Image

client = genai.Client()
organ = PIL.Image.open("media/organ.jpg")

response = client.models.generate_content(
    model="gemini-3-pro-preview",  # ✅ Gemini 3 for multimodal
    contents=["Tell me about this instrument", organ]
)
print(response.text)
```

**Alternative with File Path:**

```python
from google import genai

client = genai.Client()
image_file = client.files.upload(file="path/to/image.jpg")

response = client.models.generate_content(
    model="gemini-3-pro-preview",
    contents=[image_file, "What's in this image?"]
)
print(response.text)
```

---

## Audio Processing

```python
from google import genai

client = genai.Client()
sample_audio = client.files.upload(file="media/sample.mp3")

response = client.models.generate_content(
    model="gemini-2.5-flash",  # Flash tier for audio understanding
    contents=["Give me a summary of this audio file.", sample_audio],
)
print(response.text)
```

---

## Video Processing

```python
from google import genai
import time

client = genai.Client()

# Upload video
myfile = client.files.upload(file="media/Big_Buck_Bunny.mp4")
print(f"{myfile=}")

# Poll until video is processed (state becomes ACTIVE)
while not myfile.state or myfile.state.name != "ACTIVE":
    print("Processing video...")
    print("File state:", myfile.state)
    time.sleep(5)
    myfile = client.files.get(name=myfile.name)

# Generate content from video
response = client.models.generate_content(
    model="gemini-3-pro-preview",  # ✅ Gemini 3 for video
    contents=[myfile, "Describe this video clip"]
)
print(f"{response.text=}")
```

---

## Streaming Responses

### Basic Streaming

```python
from google import genai

client = genai.Client()
response = client.models.generate_content_stream(
    model="gemini-2.5-flash",
    contents="Write a story about a magic backpack."
)

for chunk in response:
    print(chunk.text)
    print("_" * 80)
```

### Chat Streaming with History

**Stream responses while maintaining conversation history:**

```python
from google import genai
from google.genai import types

client = genai.Client()

# Create chat with initial history
chat = client.chats.create(
    model="gemini-2.5-flash",  # ✅ Use Gemini 2.5
    history=[
        types.Content(role="user", parts=[types.Part(text="Hello")]),
        types.Content(
            role="model",
            parts=[types.Part(text="Great to meet you. What would you like to know?")]
        ),
    ],
)

# Stream first message
response = chat.send_message_stream(message="I have 2 dogs in my house.")
for chunk in response:
    print(chunk.text)
    print("_" * 80)

# Stream second message (model remembers context)
response = chat.send_message_stream(message="How many paws are in my house?")
for chunk in response:
    print(chunk.text)
    print("_" * 80)

# Get full conversation history
print(chat.get_history())
```

**Bandit CLI Enhancement Potential:**
```python
# Future: Stream responses in real-time to CLI
def query_streaming(prompt: str):
    response = client.models.generate_content_stream(
        model="gemini-3-pro-preview",
        contents=prompt
    )
    
    full_response = []
    for chunk in response:
        print(chunk.text, end="", flush=True)  # Real-time display
        full_response.append(chunk.text)
    
    return "".join(full_response)
```

### PDF Streaming

**Stream responses while processing large PDF documents:**

```python
from google import genai

client = genai.Client()
sample_pdf = client.files.upload(file="path/to/document.pdf")

response = client.models.generate_content_stream(
    model="gemini-2.5-flash",  # ✅ Use Gemini 2.5 (NOT 2.0-flash)
    contents=["Give me a summary of this document:", sample_pdf],
)

for chunk in response:
    print(chunk.text)
    print("_" * 80)
```

**Benefits of Streaming:**
- ✅ **Faster perceived speed** — User sees results immediately
- ✅ **Better UX** — Progress indication for long responses
- ✅ **Lower latency** — First token arrives faster
- ✅ **Interruptible** — Can stop generation early if needed

### Video Streaming

**Stream responses while processing video files:**

```python
from google import genai
import time

client = genai.Client()

# Upload video file
myfile = client.files.upload(file="path/to/video.mp4")
print(f"{myfile=}")

# Poll until video is completely processed (state becomes ACTIVE)
while not myfile.state or myfile.state.name != "ACTIVE":
    print("Processing video...")
    print("File state:", myfile.state)
    time.sleep(5)
    myfile = client.files.get(name=myfile.name)

# Stream video analysis
response = client.models.generate_content_stream(
    model="gemini-3-pro-preview",  # ✅ Use Gemini 3 for video (NOT 2.0-flash)
    contents=[myfile, "Describe this video clip"]
)

for chunk in response:
    print(chunk.text)
    print("_" * 80)
```

### Audio Streaming

**Stream responses while processing audio files:**

```python
from google import genai

client = genai.Client()
sample_audio = client.files.upload(file="path/to/audio.mp3")

response = client.models.generate_content_stream(
    model="gemini-2.5-flash",  # ✅ Use Gemini 2.5 (NOT 2.0-flash)
    contents=["Give me a summary of this audio file.", sample_audio],
)

for chunk in response:
    print(chunk.text)
    print("_" * 80)
```

### Image Streaming

**Stream responses while analyzing images:**

```python
from google import genai
import PIL.Image

client = genai.Client()
organ = PIL.Image.open("path/to/image.jpg")

response = client.models.generate_content_stream(
    model="gemini-3-pro-preview",  # ✅ Use Gemini 3 for multimodal (NOT 2.0-flash)
    contents=["Tell me about this instrument", organ]
)

for chunk in response:
    print(chunk.text)
    print("_" * 80)
```

### Streaming Best Practices

**1. Always Use Correct Model Names**
```python
# ✅ CORRECT
model="gemini-3-pro-preview"
model="gemini-2.5-flash"

# ❌ WRONG (from old examples)
model="gemini-2.0-flash"  # Use 2.5-flash instead
model="gemini-1.5-flash"  # PROHIBITED
```

**2. Handle File States**
```python
# Always wait for file processing before streaming
while myfile.state.name != "ACTIVE":
    time.sleep(5)
    myfile = client.files.get(name=myfile.name)
```

**3. Stream for Better UX**
```python
# Use streaming for long responses
for chunk in response:
    print(chunk.text, end="", flush=True)  # Real-time display
```

**4. Combine with Chat**
```python
# Stream within chat for conversational experience
chat = client.chats.create(model="gemini-2.5-flash")
response = chat.send_message_stream(message="Your query")
for chunk in response:
    print(chunk.text)
```

---

## File API

### Upload Files

```python
from google import genai

client = genai.Client()

# Upload file
file = client.files.upload(file="path/to/document.pdf")
print(f"Uploaded: {file.name}")

# Use uploaded file
response = client.models.generate_content(
    model="gemini-3-pro-preview",
    contents=[file, "Summarize this document"]
)
print(response.text)
```

### List Files

```python
files = client.files.list()
for f in files:
    print(f"File: {f.name}, State: {f.state}")
```

### Delete Files

```python
client.files.delete(name="files/...")
```

---

## Models API

### List Available Models

```python
from google import genai

client = genai.Client()

print("Models that support generateContent:\n")
for m in client.models.list():
    for action in m.supported_actions:
        if action == "generateContent":
            print(m.name)

print("\nModels that support embedContent:\n")
for m in client.models.list():
    for action in m.supported_actions:
        if action == "embedContent":
            print(m.name)
```

### Get Model Info

```python
from google import genai

client = genai.Client()
model_info = client.models.get(model="gemini-3-pro-preview")
print(model_info)

# Access model properties
print(f"Input token limit: {model_info.inputTokenLimit}")
print(f"Output token limit: {model_info.outputTokenLimit}")
print(f"Temperature: {model_info.temperature}")
print(f"Top P: {model_info.topP}")
```

---

## Safety Settings

```python
from google import genai

client = genai.Client()
response = client.models.generate_content(
    model="gemini-3-pro-preview",
    contents="Tell me a story",
    safety_settings=[
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        }
    ]
)
```

---

## System Instructions

```python
from google import genai

client = genai.Client()
response = client.models.generate_content(
    model="gemini-3-pro-preview",
    contents="What should I do today?",
    system_instruction="You are Bandit, the HQ Operator for LMSIFY."
)
```

---

## JSON Mode

```python
from google import genai

client = genai.Client()
response = client.models.generate_content(
    model="gemini-3-pro-preview",
    contents="List 3 popular programming languages",
    config={
        "response_mime_type": "application/json",
        "response_schema": {
            "type": "object",
            "properties": {
                "languages": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            }
        }
    }
)
print(response.text)  # Returns JSON
```

---

## Thinking Mode (Gemini 3 Pro)

```python
from google import genai

client = genai.Client()
response = client.models.generate_content(
    model="gemini-3-pro-preview",
    contents="Solve this complex math problem...",
    config={
        "thinking_config": {
            "include_thoughts": True,
            "thinking_level": "HIGH"
        }
    }
)

# Access thoughts (if available)
print(response.thoughts)  # Model's internal reasoning
print(response.text)      # Final answer
```

---

## Comparison: google.genai vs vertexai

### google.genai (Simpler)

```python
from google import genai

client = genai.Client()
response = client.models.generate_content(
    model="gemini-3-pro-preview",
    contents="Hello"
)
print(response.text)
```

### vertexai (More Control - Bandit's Current Approach)

```python
import vertexai
from vertexai.generative_models import GenerativeModel

vertexai.init(project="...", location="global")
model = GenerativeModel("gemini-3-pro-preview")
response = model.generate_content("Hello")
print(response.text)
```

---

## When to Use Which

### Use `google.genai` when:
- Quick prototyping
- Simple scripts
- Testing new features
- Learning Gemini API
- File upload needed (simpler API)

### Use `vertexai` when:
- Production deployment (Reasoning Engine)
- Vertex AI features needed (caching, etc.)
- Enterprise integration
- Fine-grained control required
- **Currently:** All Bandit deployments

---

## Bandit Integration Potential

### Future Enhancement: Hybrid Approach

```python
# Production (Reasoning Engine): Use vertexai
class BanditEngine:
    def __init__(self):
        vertexai.init(project=..., location='global')
        self.model = GenerativeModel("gemini-3-pro-preview")
    
    def query(self, prompt):
        return self.model.generate_content(prompt).text

# Development/Testing: Use google.genai
from google import genai
client = genai.Client()
response = client.models.generate_content(
    model="gemini-3-pro-preview",
    contents="Test query"
)
```

---

## Advanced Features

### Code Execution

**Model Support:** Gemini 3 Pro, Gemini 2.5 Pro  
**Capability:** Model can write and execute Python code to solve problems

```python
from google import genai
from google.genai import types

client = genai.Client()
response = client.models.generate_content(
    model="gemini-3-pro-preview",  # ✅ Use Gemini 3 for code execution
    contents=(
        "Write and execute code that calculates the sum of the first 50 prime numbers. "
        "Ensure that only the executable code and its resulting output are generated."
    ),
)

# Each part may contain text, executable code, or an execution result
for part in response.candidates[0].content.parts:
    print(part, "\n")

print("-" * 80)
# The .text accessor concatenates the parts into markdown-formatted text
print("\n", response.text)
```

**Use Cases:**
- Mathematical calculations
- Data analysis
- Algorithm implementation
- Scientific computations

---

### Function Calling (Tool Use)

**Model Support:** All Gemini 2.5 and 3 models  
**Capability:** Model can call Python functions you provide as tools

```python
from google import genai
from google.genai import types

client = genai.Client()

# Define tool functions
def add(a: float, b: float) -> float:
    """returns a + b."""
    return a + b

def subtract(a: float, b: float) -> float:
    """returns a - b."""
    return a - b

def multiply(a: float, b: float) -> float:
    """returns a * b."""
    return a * b

def divide(a: float, b: float) -> float:
    """returns a / b."""
    return a / b

# Create chat with tools enabled
chat = client.chats.create(
    model="gemini-2.5-flash",  # ✅ Flash tier supports function calling
    config=types.GenerateContentConfig(
        tools=[add, subtract, multiply, divide]
    ),
)

response = chat.send_message(
    message="I have 57 cats, each owns 44 mittens, how many mittens is that in total?"
)
print(response.text)
# Model will call multiply(57, 44) and return: "That's 2508 mittens in total."
```

**Bandit Integration Potential:**
```python
# Future: Bandit could use function calling for HQ operations
def create_intake_id(directive_type: str, priority: str) -> str:
    """Generate intake ID for directive."""
    # Implementation
    return f"INTAKE-{directive_type}-{priority}-{timestamp}"

def log_to_ritual_journal(entry: str) -> str:
    """Log entry to ritual journal."""
    # Implementation
    return "Logged successfully"

# Enable in chat
chat = client.chats.create(
    model="gemini-3-pro-preview",
    config=types.GenerateContentConfig(
        tools=[create_intake_id, log_to_ritual_journal]
    )
)
```

---

### Generation Config

**Complete control over model output parameters:**

```python
from google import genai
from google.genai import types

client = genai.Client()
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Tell me a story about a magic backpack.",
    config=types.GenerateContentConfig(
        candidate_count=1,           # Number of responses to generate
        stop_sequences=["x"],        # Stop generation at these sequences
        max_output_tokens=20,        # Limit response length
        temperature=1.0,             # Creativity level (0.0-2.0)
        top_p=0.95,                  # Nucleus sampling
        top_k=40,                    # Top-k sampling
        presence_penalty=0.0,        # Penalize repeated concepts
        frequency_penalty=0.0        # Penalize repeated tokens
    ),
)
print(response.text)
```

**Parameter Guide:**

| Parameter | Range | Effect |
|-----------|-------|--------|
| **temperature** | 0.0 - 2.0 | Higher = more creative/varied |
| **top_p** | 0.0 - 1.0 | Nucleus sampling threshold |
| **top_k** | 1 - 100+ | Consider top K tokens |
| **max_output_tokens** | 1 - 65536 | Maximum response length |
| **stop_sequences** | List of strings | Stop generation at these |
| **presence_penalty** | -2.0 - 2.0 | Discourage repeated concepts |
| **frequency_penalty** | -2.0 - 2.0 | Discourage repeated tokens |

**Bandit's Current Config:**
```python
# In deploy_reasoning_engine.py
generation_config = {
    "temperature": 1.0,
    "response_modalities": ["IMAGE", "TEXT"]  # For image generation
}
```

---

### Safety Settings

**Control content filtering and safety thresholds:**

```python
from google import genai
from google.genai import types

client = genai.Client()

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Your prompt here",
    config=types.GenerateContentConfig(
        safety_settings=[
            types.SafetySetting(
                category="HARM_CATEGORY_HATE_SPEECH",
                threshold="BLOCK_MEDIUM_AND_ABOVE",
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_HARASSMENT",
                threshold="BLOCK_ONLY_HIGH"
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                threshold="BLOCK_MEDIUM_AND_ABOVE"
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_DANGEROUS_CONTENT",
                threshold="BLOCK_MEDIUM_AND_ABOVE"
            ),
        ]
    ),
)

# Handle blocked content
try:
    print(response.text)
except Exception:
    print("No information generated by the model.")
    print("Safety ratings:", response.candidates[0].safety_ratings)
```

**Safety Categories:**
- `HARM_CATEGORY_HARASSMENT`
- `HARM_CATEGORY_HATE_SPEECH`
- `HARM_CATEGORY_SEXUALLY_EXPLICIT`
- `HARM_CATEGORY_DANGEROUS_CONTENT`
- `HARM_CATEGORY_CIVIC_INTEGRITY`

**Thresholds:**
- `BLOCK_NONE` — No blocking
- `BLOCK_ONLY_HIGH` — Block only high-probability harm
- `BLOCK_MEDIUM_AND_ABOVE` — Block medium and high (default)
- `BLOCK_LOW_AND_ABOVE` — Most restrictive

**Bandit's Recommended Settings:**
```python
# For LMSIFY HQ operations
safety_settings = [
    types.SafetySetting(
        category="HARM_CATEGORY_HARASSMENT",
        threshold="BLOCK_MEDIUM_AND_ABOVE"
    ),
    types.SafetySetting(
        category="HARM_CATEGORY_HATE_SPEECH",
        threshold="BLOCK_MEDIUM_AND_ABOVE"
    ),
    types.SafetySetting(
        category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
        threshold="BLOCK_MEDIUM_AND_ABOVE"
    ),
    types.SafetySetting(
        category="HARM_CATEGORY_DANGEROUS_CONTENT",
        threshold="BLOCK_MEDIUM_AND_ABOVE"
    ),
]
```

---

### Chat History Management

**Maintain conversation context across multiple turns:**

```python
from google import genai
from google.genai import types

client = genai.Client()

# Create chat with initial history
chat = client.chats.create(
    model="gemini-2.5-flash",
    history=[
        types.Content(
            role="user",
            parts=[types.Part(text="Hello")]
        ),
        types.Content(
            role="model",
            parts=[types.Part(text="Great to meet you. What would you like to know?")]
        ),
    ],
)

# Continue conversation
response = chat.send_message(message="I have 2 dogs in my house.")
print(response.text)

response = chat.send_message(message="How many paws are in my house?")
print(response.text)  # Model remembers: 2 dogs × 4 paws = 8 paws
```

**Bandit Future Enhancement:**
```python
# Maintain conversation history for ongoing HQ operations
bandit_chat = client.chats.create(
    model="gemini-3-pro-preview",
    history=load_conversation_history(),  # From HQ/memory/conversations.json
    config=types.GenerateContentConfig(
        system_instruction="You are Bandit, the HQ Operator for LMSIFY."
    )
)
```

---

### Context Caching

**Cache large contexts to reduce latency and cost:**

⚠️ **CRITICAL:** Example uses `gemini-1.5-flash-001` which is **PROHIBITED**. Always replace with Gemini 2.5 or 3:

```python
from google import genai
from google.genai import types

client = genai.Client()
document = client.files.upload(file="path/to/document.txt")

# ✅ CORRECT: Use Gemini 2.5 or 3
model_name = "gemini-2.5-pro"  # NOT gemini-1.5-flash-001

# Create cached content
cache = client.caches.create(
    model=model_name,
    config=types.CreateCachedContentConfig(
        contents=[document],
        system_instruction="You are an expert analyzing transcripts.",
    ),
)
print(f"Cache created: {cache.name}")

# Use cached content in subsequent requests
response = client.models.generate_content(
    model=model_name,
    contents="Please summarize this transcript",
    config=types.GenerateContentConfig(
        cached_content=cache.name
    ),
)
print(response.text)
```

**When to Use Caching:**
- Large documents processed multiple times
- System instructions used repeatedly
- Brand briefs, manuals loaded in every session
- Frequently accessed HQ intelligence files

**Bandit Caching Strategy (Future):**
```python
# Cache Bandit's core context
bandit_cache = client.caches.create(
    model="gemini-3-pro-preview",
    config=types.CreateCachedContentConfig(
        contents=[
            load_file("HQ/memory/gemini3_training_manual.md"),
            load_file("HQ/intelligence/brand-brief.md"),
            load_file("HQ/intelligence/initiative-map.md"),
        ],
        system_instruction="You are Bandit, the HQ Operator for LMSIFY."
    )
)

# Reuse cache for faster, cheaper queries
response = client.models.generate_content(
    model="gemini-3-pro-preview",
    contents="What's the current status of Project X?",
    config=types.GenerateContentConfig(cached_content=bandit_cache.name)
)
```

**Cache Benefits:**
- ✅ Reduced latency (faster responses)
- ✅ Lower cost (cached tokens charged at reduced rate)
- ✅ Consistent context across requests

---

## Best Practices

### 1. Always Use Gemini 2.5 or 3

```python
# ✅ CORRECT
client.models.generate_content(model="gemini-3-pro-preview", ...)
client.models.generate_content(model="gemini-2.5-flash", ...)

# ❌ WRONG
client.models.generate_content(model="gemini-1.5-flash", ...)  # PROHIBITED
```

### 2. Handle File States

```python
# Always check file state before using
file = client.files.upload(file="video.mp4")
while file.state.name != "ACTIVE":
    time.sleep(5)
    file = client.files.get(name=file.name)

# Now file is ready
response = client.models.generate_content(model="...", contents=[file, "..."])
```

### 3. Use Streaming for Long Responses

```python
# Stream for better UX
response = client.models.generate_content_stream(
    model="gemini-2.5-flash",
    contents="Write a long story..."
)
for chunk in response:
    print(chunk.text, end="")  # Real-time display
```

### 4. Clean Up Files

```python
# Delete uploaded files when done
client.files.delete(name=file.name)
```

---

## Error Handling

```python
from google import genai

client = genai.Client()

try:
    response = client.models.generate_content(
        model="gemini-3-pro-preview",
        contents="Hello"
    )
    print(response.text)
except Exception as e:
    print(f"Error: {e}")
    # Handle error appropriately
```

---

## Quick Reference

### Supported Modalities Input

| Modality | Method | Model Support |
|----------|--------|---------------|
| Text | Direct string | All models |
| Image | PIL.Image or file upload | Gemini 3 Pro, 2.5 Flash |
| Audio | File upload | Gemini 2.5 Flash |
| Video | File upload | Gemini 3 Pro, 2.5 Flash |
| PDF | File upload | Gemini 3 Pro, 2.5 Pro |

### Supported Modalities Output

| Modality | Config | Model Support |
|----------|--------|---------------|
| Text | Default | All models |
| Image | response_modalities=["IMAGE"] | Gemini 3 Pro Image |
| Audio | speechConfig | Gemini 2.5 Flash |

---

## Resources

- **Official Docs:** https://ai.google.dev/api
- **PyPI:** https://pypi.org/project/google-generativeai/
- **GitHub:** https://github.com/google/generative-ai-python

---

**Key Takeaway:** `google.genai` offers a simpler, cleaner API for Gemini access. While Bandit currently uses `vertexai` for Reasoning Engine deployment, `google.genai` is excellent for testing, prototyping, and future CLI enhancements.

**Remember:** ❌ **NEVER USE GEMINI 1.5** ✅ **ONLY GEMINI 2.5 OR 3**
