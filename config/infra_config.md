# Bandit Infrastructure Config
> Reference for model endpoints and deployment settings.

## Model Hierarchy

| Tier | Model | Use Case |
|------|-------|----------|
| **Smoke Tests** | `gemini-2.5-flash-lite-preview-06-17` | Quick validation, low-cost iteration |
| **Standard** | `gemini-2.5-flash-preview-04-17` | Balanced speed/quality |
| **Production** | `gemini-2.5-pro-preview-06-05` | Complex reasoning, high-stakes |
| **Premium** | `gemini-3-pro-preview` | Cutting-edge, global endpoint |
| **Image Gen** | `gemini-3-pro-image-preview` | Native image generation |

## Endpoint Configuration

```python
# Global endpoint models (location='global')
GLOBAL_MODELS = [
    "gemini-3-pro-preview",
    "gemini-3-pro-image-preview"
]

# Regional endpoint models (location='us-central1')
REGIONAL_MODELS = [
    "gemini-2.5-flash-lite-preview-06-17",
    "gemini-2.5-flash-preview-04-17", 
    "gemini-2.5-pro-preview-06-05"
]
```

## Local Development (`agents.py`)

```python
import vertexai
from vertexai.generative_models import GenerativeModel

# For global models
vertexai.init(project="your-project", location="global")

# For regional models  
vertexai.init(project="your-project", location="us-central1")
```

## Deployment (`deploy.py`)

```python
# Reasoning Engine deployment
from vertexai import agent_engines

engine = agent_engines.ReasoningEngine.create(
    display_name="bandit-agent",
    # ... config
)
```

## Environment Variables

```bash
# Required
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json

# Optional
VERTEX_AI_SEARCH_DATA_STORE_ID=your-datastore-id
GCS_BUCKET=your-bucket-name
```

## Quick Reference

| Toggle | File | Purpose |
|--------|------|---------|
| Model selection | `agents.py` | Switch between tiers |
| Location routing | `deploy_reasoning_engine.py` | Global vs regional |
| RAG integration | `bandit_cli.py` | Vertex AI Search |
