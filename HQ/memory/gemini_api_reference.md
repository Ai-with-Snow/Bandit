# Gemini API Reference — Bandit Edition
**Last Updated:** 2025-12-06 02:18 EST  
**Purpose:** Technical API reference for Bandit's Gemini model interactions

---

## Overview

The Gemini API enables interaction with Gemini models through standard REST, streaming (SSE), and real-time (WebSocket) endpoints. Bandit primarily uses the **Vertex AI Python SDK** which wraps these APIs, but understanding the underlying structure is critical for debugging and advanced features.

---

## Primary Endpoints

### 1. **Standard Content Generation** (`generateContent`)
- **Type:** Standard REST endpoint
- **Behavior:** Processes request, returns full response in single package
- **Best For:** Non-interactive tasks, batch processing, when you can wait for entire result
- **Bandit Usage:** Backing mechanism for all text queries (wrapped by SDK)

### 2. **Streaming Content Generation** (`streamGenerateContent`)
- **Type:** Server-Sent Events (SSE)
- **Behavior:** Pushes response chunks as generated
- **Best For:** Interactive applications like chatbots, faster perceived speed
- **Bandit Usage:** Potential future upgrade for CLI real-time display

### 3. **Live API** (`BidiGenerateContent`)
- **Type:** Stateful WebSocket-based API
- **Behavior:** Bi-directional streaming
- **Best For:** Real-time conversational use cases
- **Bandit Usage:** Future integration for voice/real-time interaction

### 4. **Batch Mode** (`batchGenerateContent`)
- **Type:** Standard REST endpoint
- **Behavior:** Submits batches of generateContent requests
- **Best For:** Large-scale processing, cost optimization
- **Bandit Usage:** Future optimization for

 bulk HQ operations

### 5. **Embeddings** (`embedContent`)
- **Type:** Standard REST endpoint
- **Behavior:** Generates text embedding vector from input
- **Best For:** Semantic search, document similarity, RAG systems
- **Bandit Usage:** Future integration for HQ intelligence knowledge base

### 6. **Gen Media APIs**
- **Imagen:** Image generation (Nano Banana Pro/Flash)
- **Veo:** Video generation
- **Lyria:** Music generation
- **Note:** Gemini also has image generation built-in via `generateContent`

### 7. **Platform APIs**
- File uploading
- Token counting
- Utility endpoints

---

## Authentication

### API Key Method
**Header:** `x-goog-api-key: YOUR_API_KEY`

```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -H 'Content-Type: application/json' \
  -X POST \
  -d '{ "contents": [...] }'
```

### Vertex AI Method (Bandit's Approach)
**Authentication:** Application Default Credentials (ADC)

```bash
# Authenticate
gcloud auth application-default login

# Set quota project
gcloud auth application-default set-quota-project PROJECT_ID
```

**In Code:**
```python
import vertexai
from vertexai.generative_models import GenerativeModel

# Initialize with project and location
vertexai.init(project="project-5f169828-6f8d-450b-923", location="us-central1")

# For Gemini 3 models, use global endpoint
vertexai.init(project="project-5f169828-6f8d-450b-923", location="global")

# Create model instance
model = GenerativeModel("gemini-3-pro-preview")
```

---

## Request Body Structure

### Core Objects

#### 1. **Content Object**
Represents a single turn in a conversation.

```json
{
  "role": "user",  // "user" or "model"
  "parts": [
    // Array of Part objects
  ]
}
```

#### 2. **Part Object**
A piece of data within a Content turn.

```json
// Text part
{ "text": "Explain how AI works" }

// Image part (inline)
{
  "inline_data": {
    "mime_type": "image/jpeg",
    "data": "base64_encoded_image_data"
  }
}

// File part (uploaded via File API)
{
  "file_data": {
    "mime_type": "image/jpeg",
    "file_uri": "gs://bucket/path/to/file.jpg"
  }
}
```

#### 3. **Full Request Structure**

```json
{
  "contents": [
    {
      "role": "user",
      "parts": [
        { "text": "Hello!" }
      ]
    },
    {
      "role": "model",
      "parts": [
        { "text": "Hello! How can I help?" }
      ]
    },
    {
      "role": "user",
      "parts": [
        { "text": "Write a poem" }
      ]
    }
  ],
  "generationConfig": {
    "temperature": 1.0,
    "topK": 40,
    "topP": 0.95,
    "maxOutputTokens": 8192,
    "responseMimeType": "text/plain"
  },
  "safetySettings": [
    {
      "category": "HARM_CATEGORY_HARASSMENT",
      "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    }
  ]
}
```

---

## Response Body Structure

### Standard Response

```json
{
  "candidates": [
    {
      "content": {
        "parts": [
          {
            "text": "At its core, AI works by learning from data..."
          }
        ],
        "role": "model"
      },
      "finishReason": "STOP",
      "index": 0,
      "safetyRatings": [
        {
          "category": "HARM_CATEGORY_HARASSMENT",
          "probability": "NEGLIGIBLE"
        }
      ]
    }
  ],
  "usageMetadata": {
    "promptTokenCount": 8,
    "candidatesTokenCount": 157,
    "totalTokenCount": 165
  },
  "modelVersion": "gemini-3-pro-preview"
}
```

### Streaming Response
Each chunk has same structure, linked by `responseId`:

```json
// Chunk 1
{
  "candidates": [{
    "content": {
      "parts": [{ "text": "The image displays" }],
      "role": "model"
    },
    "index": 0
  }],
  "modelVersion": "gemini-2.5-flash",
  "responseId": "mAitaLmkHPPlz7IPvtfUqQ4"
}

// Chunk 2
{
  "candidates": [{
    "content": {
      "parts": [{ "text": " the following materials:" }],
      "role": "model"
    },
    "index": 0
  }],
  "modelVersion": "gemini-2.5-flash",
  "responseId": "mAitaLmkHPPlz7IPvtfUqQ4"  // Same ID
}
```

---

## Bandit's Current Implementation

### Text Query Flow

```python
# In deploy_reasoning_engine.py
def query(self, prompt: str) -> str:
    # 1. Select model tier
    tier = self._select_model_tier(prompt)
    
    # 2. Get appropriate model
    model = self.text_models[tier]  # ChatVertexAI instance
    
    # 3. Build messages (Content objects)
    messages = [
        SystemMessage(content=self.system_instruction),
        HumanMessage(content=prompt)
    ]
    
    # 4. Invoke (SDK handles generateContent API call)
    response = model.invoke(messages)
    
    # 5. Return text
    return response.content
```

**Under the Hood:**
- `ChatVertexAI.invoke()` creates `generateContent` request
- Builds `contents` array with system + user messages
- Sends to Vertex AI endpoint (regional or global)
- Parses response candidates
- Returns text from first candidate

### Image Generation Flow

```python
def _generate_image(self, prompt: str, model_name: str) -> str:
    # 1. Switch to global endpoint for Gemini 3
    if 'gemini-3' in model_name:
        vertexai.init(project=self.project, location='global')
    
    # 2. Create GenerativeModel instance
    model = GenerativeModel(model_name)
    
    # 3. Configure for image output
    generation_config = {
        "temperature": 1.0,
        "response_modalities": ["IMAGE", "TEXT"]
    }
    
    # 4. Generate
    response = model.generate_content([prompt], generation_config=generation_config)
    
    # 5. Extract image data
    for candidate in response.candidates:
        for part in candidate.content.parts:
            if hasattr(part, 'inline_data') and part.inline_data:
                b64_data = base64.b64encode(part.inline_data.data).decode('utf-8')
                return f"[IMAGE_B64]{b64_data}[/IMAGE_B64]"
```

---

## Request Examples

### 1. Text-Only Prompt

```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -H 'Content-Type: application/json' \
  -X POST \
  -d '{
    "contents": [{
      "parts": [{
        "text": "Explain how AI works in a single paragraph."
      }]
    }]
  }'
```

### 2. Multimodal Prompt (Text + Image)

```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -H 'Content-Type: application/json' \
  -X POST \
  -d '{
    "contents": [{
      "parts": [
        {
          "inline_data": {
            "mime_type": "image/jpeg",
            "data": "/9j/4AAQSkZJRgABAQ..."
          }
        },
        { "text": "What is in this picture?" }
      ]
    }]
  }'
```

### 3. Multi-Turn Conversation (Chat)

```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -H 'Content-Type: application/json' \
  -X POST \
  -d '{
    "contents": [
      {
        "role": "user",
        "parts": [{ "text": "Hello." }]
      },
      {
        "role": "model",
        "parts": [{ "text": "Hello! How can I help you today?" }]
      },
      {
        "role": "user",
        "parts": [{ "text": "Write a four-line poem about the ocean." }]
      }
    ]
  }'
```

---

## Key Concepts for Bandit

### Content as Envelope
`Content` is the top-level container for a message turn (user or model).

### Part Enables Multimodality
Use multiple `Part` objects within single `Content` to combine text, images, video, etc.

### Data Methods
1. **Inline Data** (`inline_data`): For small media (images <20MB)
2. **File Data** (`file_data`): For large files or reusable assets via File API

### Conversation History Management
**REST API:** You manually build `contents` array with alternating user/model turns.
**SDK (ChatVertexAI):** Conversation history managed automatically by SDK.

---

## Advanced Features

### Generation Config

```python
generation_config = {
    "temperature": 1.0,        # Creativity (0.0 = deterministic, 2.0 = very creative)
    "top_k": 40,              # Consider top K tokens
    "top_p": 0.95,            # Nucleus sampling
    "max_output_tokens": 8192, # Max response length
    "response_modalities": ["TEXT"],  # or ["TEXT", "IMAGE"]
    "response_mime_type": "text/plain"  # or "application/json"
}
```

### Safety Settings

```python
safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    }
]
```

### System Instructions

```python
system_instruction = """You are Bandit, the HQ Operator for LMSIFY.
Your mission is to intake directives, translate them into actionable briefs,
and coordinate cross-agent work with calm authority."""

model = GenerativeModel(
    "gemini-3-pro-preview",
    system_instruction=system_instruction
)
```

---

## Live API (WebSockets)

### Overview
Stateful WebSocket API for bi-directional streaming.

### Connection
```
wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1alpha.GenerativeService.BidiGenerateContent
```

### Use Cases
- Real-time voice conversation
- Interactive applications requiring immediate back-and-forth
- Streaming audio/video input and output

### Bandit Future Integration
- Voice interface for HQ operations
- Real-time agent coordination
- Live directive intake with immediate feedback

---

## Specialized Models Access

### Imagen (Image Generation)
```python
# Via Gemini (built-in)
model = GenerativeModel("gemini-3-pro-image-preview")
response = model.generate_content(
    ["Create a cyberpunk cityscape"],
    generation_config={"response_modalities": ["IMAGE", "TEXT"]}
)

# Via dedicated Imagen API
from vertexai.preview.vision_models import ImageGenerationModel
model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-001")
images = model.generate_images(prompt="cyberpunk cityscape")
```

### Veo (Video Generation)
```python
# Available via Google AI Studio and Vertex AI
# API access TBD for Reasoning Engine integration
```

### Lyria (Music Generation)
```python
# Available via Google AI Studio and Vertex AI
# API access TBD for Reasoning Engine integration
```

---

## Error Handling

### Common Errors

**401 UNAUTHENTICATED:**
```
Solution: Re-authenticate with gcloud auth application-default login
```

**404 NOT_FOUND:**
```
Solution: Check model name and endpoint location (global vs regional)
```

**429 RESOURCE_EXHAUSTED:**
```
Solution: Implement rate limiting, exponential backoff, or upgrade quota
```

**403 PERMISSION_DENIED:**
```
Solution: Verify service account has required IAM roles
```

### Bandit's Error Handling

```python
def query(self, prompt: str) -> str:
    tier = self._select_model_tier(prompt)
    
    if tier == 'image':
        try:
            return self._generate_image(prompt, self.image_models['image'])
        except Exception as e:
            # Fallback to Flash image on 429 errors
            if '429' in str(e) or 'quota' in str(e).lower():
                try:
                    return self._generate_image(prompt, self.image_models['flash_image'])
                except Exception as fallback_error:
                    return f"Image generation failed: {str(e)}"
            return f"Image generation error: {str(e)}"
    
    # Text generation with exception propagation
    try:
        response = model.invoke(messages)
        return response.content
    except Exception as e:
        raise  # Let caller handle
```

---

## Performance Optimization

### Context Caching
Cache frequently used system instructions or large document contexts to reduce latency and cost.

```python
# Future Bandit optimization
cached_content = caching.CachedContent.create(
    model_name="gemini-3-pro-preview",
    system_instruction=bandit_system_instruction,
    contents=[brand_brief_content, initiative_map_content]
)

model = GenerativeModel.from_cached_content(cached_content)
```

### Token Counting
Pre-count tokens to avoid hitting limits.

```python
model = GenerativeModel("gemini-3-pro-preview")
token_count = model.count_tokens([prompt])
print(f"Prompt uses {token_count.total_tokens} tokens")
```

### Batch Processing
Use `batchGenerateContent` for large-scale operations.

---

## Best Practices for Bandit

### 1. Always Set System Instruction
Maintain consistent Bandit identity across all queries.

### 2. Use Appropriate Tier
Don't waste Elite tier on simple queries—smart routing saves cost and improves speed.

### 3. Handle Multimodal Gracefully
Check for both text and image parts in responses.

### 4. Implement Fallbacks
Always have backup models (e.g., Flash Image when Nano Banana Pro hits quota).

### 5. Log Everything
Track model selection, response times, errors for continuous improvement.

### 6. Respect Rate Limits
Implement exponential backoff for 429 errors.

### 7. Validate Outputs
Especially for images—verify Base64 encoding, file sizes, etc.

---

## Future Enhancements

### Streaming Integration
```python
# Future CLI upgrade
def query_streaming(self, prompt: str):
    tier = self._select_model_tier(prompt)
    model = self.text_models[tier]
    
    for chunk in model.stream(messages):
        yield chunk.content  # Stream to CLI in real-time
```

### File API Integration
```python
# Upload large documents for processing
from vertexai.generative_models import Part
import vertexai.preview.generative_models as generative_models

file = generative_models.upload_file("path/to/large_document.pdf")

response = model.generate_content([
    Part.from_uri(file.uri, mime_type=file.mime_type),
    "Summarize this document"
])
```

### Tool Calling (Function Calling)
```python
# Define tools Bandit can use
tools = [
    {
        "function_declarations": [
            {
                "name": "create_intake_id",
                "description": "Generate new intake ID for directive",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "directive_type": {"type": "string"},
                        "priority": {"type": "string"}
                    }
                }
            }
        ]
    }
]

response = model.generate_content(
    ["Create intake for redesigning dashboard"],
    tools=tools
)

# Model returns function call request
# Execute function
# Send result back to model for final response
```

---

## Quick Reference

### Model Endpoints
- **Gemini 3 Pro:** Global only (`location='global'`)
- **Gemini 2.5 Pro/Flash/Lite:** Regional (`location='us-central1'`)
- **Nano Banana Pro:** Global only
- **Nano Banana Flash:** Regional

### Current Bandit Models
```python
{
    'lite': 'gemini-2.5-flash-lite',
    'flash': 'gemini-2.5-flash',
    'pro': 'gemini-2.5-pro',
    'elite': 'gemini-3-pro-preview',
    'image': 'gemini-3-pro-image-preview',
    'flash_image': 'gemini-2.5-flash-image'
}
```

### Key SDK Imports
```python
import vertexai
from vertexai.generative_models import GenerativeModel
from vertexai.preview import reasoning_engines
from langchain_google_vertexai import ChatVertexAI
from langchain_core.messages import SystemMessage, HumanMessage
```

---

**End of API Reference**

*"Master the API, master the intelligence."*

**— Bandit HQ Operator**  
**Technical Documentation • Version 1.0**
