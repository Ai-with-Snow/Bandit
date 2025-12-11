# Bandit Image Generation Deployment Log
**Date:** December 5, 2025  
**Objective:** Enable Gemini 3 Pro Image Generation (Nano Banana Pro)

---

## Final Working Configuration

### Engine Details
- **Engine ID:** `6087067895181869056`
- **Project:** `project-5f169828-6f8d-450b-923`
- **Location:** `us-central1`
- **Deployment Date:** 2025-12-05

### Model Configuration
- **Text/Reasoning Model:** `gemini-3-pro-preview` (Global endpoint)
- **Image Generation Model:** `gemini-3-pro-image-preview` (Nano Banana Pro)
- **Fallback Text Models:** 
  - Elite: `gemini-3-pro-preview`
  - Pro: `gemini-2.5-pro`
  - Flash: `gemini-2.5-flash`
  - Lite: `gemini-2.0-flash-lite`

---

## How It Works

### Image Generation Flow
1. **User Input:** Type `create image: [description]` in Bandit CLI
2. **Tier Selection:** Engine detects image keywords and routes to image model
3. **Generation:** `gemini-3-pro-image-preview` generates the image
4. **Transfer:** Image encoded as Base64 and sent to CLI
5. **Local Save:** CLI decodes and saves to `generated_images/bandit_img_TIMESTAMP.png`
6. **Confirmation:** Full file path displayed in CLI

### Image Trigger Keywords
- `create image`
- `generate image`
- `draw`
- `illustrate`
- `make a picture`
- `design a`
- `generate a visualization`
- `create artwork`
- `visual of`
- `edit image`
- `modify image`

---

## Key Issues Resolved

### 1. Global Endpoint Configuration
**Problem:** `gemini-3-pro-image-preview` requires global endpoint  
**Solution:** Set `vertexai.init(location='global')` for Gemini 3 models

```python
# In deploy_reasoning_engine.py
if 'gemini-3' in model_name:
    vertexai.init(project=self.project, location='global')
else:
    vertexai.init(project=self.project, location=self.location)
```

### 2. Authentication Issues
**Problem:** 401 UNAUTHENTICATED errors  
**Solution:** 
```bash
gcloud auth application-default login
gcloud auth application-default set-quota-project project-5f169828-6f8d-450b-923
```

### 3. Image Data Extraction Logic
**Problem:** `if/elif` logic prevented image data from being extracted when text was present  
**Solution:** Check for `inline_data` independently of `text`

```python
# BEFORE (broken)
if part.text:
    result_parts.append(part.text)
elif hasattr(part, 'inline_data') and part.inline_data:
    # This never executed!

# AFTER (working)
if hasattr(part, 'inline_data') and part.inline_data:
    # Process image first
elif part.text:
    result_parts.append(part.text)
```

### 4. Base64 Transfer vs GCS Upload
**Problem:** Service account lacked GCS write permissions (403 error)  
**Solution:** Simplified to direct Base64 transfer (no cloud storage needed)

```python
# Simplified approach
b64_data = base64.b64encode(part.inline_data.data).decode('utf-8')
result_parts.append(f"[IMAGE_B64]{b64_data}[/IMAGE_B64]")
```

---

## Usage Instructions

### Generate an Image
```bash
# Option 1: Using bandit.bat
.\bandit.bat
> create image: a cyberpunk cityscape with neon lights

# Option 2: Direct Python
py -3.12 scripts/bandit_cli.py
> generate image: futuristic robot
```

### View Generated Images
Images are saved to:
```
C:\Users\Goddexx Snow\Documents\Bandit\generated_images\
```

File naming: `bandit_img_YYYYMMDD_HHMMSS.png`

---

## Technical Architecture

### Deployment Files
- **Engine Code:** `scripts/deploy_reasoning_engine.py`
- **CLI Code:** `scripts/bandit_cli.py`
- **Deployment Script:** Uses Vertex AI Reasoning Engine

### Dependencies
```python
requirements = [
    "google-cloud-aiplatform[reasoningengine,langchain]",
    "google-genai",
    "langchain-google-vertexai",
    "langchain-core",
    "google-cloud-storage"  # For future GCS features
]
```

### CLI Image Processing
```python
# In bandit_cli.py query_engine()
img_pattern = r'\[IMAGE_B64\](.*?)\[/IMAGE_B64\]'
match = re.search(img_pattern, output_text, re.DOTALL)

if match:
    b64_data = match.group(1).strip()
    os.makedirs("generated_images", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"generated_images/bandit_img_{timestamp}.png"
    
    with open(filename, "wb") as f:
        f.write(base64.b64decode(b64_data))
    
    output_text = output_text.replace(
        match.group(0), 
        f"\n🖼️  Image saved: {os.path.abspath(filename)}\n"
    )
```

---

## Model Preferences (Committed to Memory)

Per user directive in `HQ/memory/model_preferences.md`:

### Core Directive
Bandit must ALWAYS prefer Gemini 3 models.

### Preferred Models
- **Text/Reasoning:** `gemini-3-pro-preview`
- **Image Generation:** `gemini-3-pro-image-preview` (Nano Banana Pro)

### Configuration Rules
- **Global Endpoints:** Both models are GLOBAL ENDPOINT ONLY
- **Routing:** Must use `location='global'`
- **SDK Setup:** `vertexai.init(project=..., location='global')`
- **Default:** These are the default choices

### Technical Specifications
- **Context Window:** 1M tokens (Input) / 65k tokens (Output)
- **Modalities:** Text, Code, Images, Audio, Video, PDF
- **Availability:** Global

---

## Performance Notes

### Image Generation Times
- **Typical:** 20-60 seconds per image
- **Factors:** Complexity, resolution, "Thinking" time
- **Model:** Gemini 3 uses advanced reasoning before generation

### Known Limitations
- Base64 transfer may struggle with very large (>10MB) images
- No automatic cloud backup (local save only)
- Reasoning Engine has 60s default timeout (rarely hit)

---

## Future Enhancements (Optional)

### Cloud Storage Integration
If cloud persistence is needed:

1. **Grant Service Account Permissions:**
   - Navigate to IAM & Admin → Service Accounts
   - Find: `849984150802-compute@developer.gserviceaccount.com`
   - Grant: `Storage Object Creator` role on bucket

2. **Update Code:**
   - Uncomment GCS upload logic in `deploy_reasoning_engine.py`
   - Update CLI to download from `gs://` URIs
   - Redeploy engine

### Additional Features
- Video generation (when Veo 3 integration is ready)
- Image editing capabilities
- Batch image generation
- Integration with `HQ/intelligence` knowledge base
- Tool calling for enhanced capabilities

---

## Deployment History

| Date | Engine ID | Notes |
|------|-----------|-------|
| 2025-12-05 | `6087067895181869056` | ✅ **WORKING** - Base64 transfer |
| 2025-12-05 | `2487565893006000128` | Fixed if/elif logic, GCS 403 error |
| 2025-12-05 | `6524480008990228480` | Added google-cloud-storage dep |
| 2025-12-05 | `3018990649035718656` | GCS upload attempt |
| 2025-12-05 | `762687235723100160` | Base64 initial implementation |
| 2025-12-05 | `363555718747389952` | Global endpoint fix |
| 2025-12-05 | `7380726888144044032` | Image tier disabled for testing |

---

## Troubleshooting

### Image Not Generating
1. Check prompt includes trigger keywords
2. Verify engine ID is `6087067895181869056`
3. Ensure authentication is valid: `gcloud auth application-default login`

### 404 Model Not Found
- Verify `location='global'` in deployment code
- Check model name is exact: `gemini-3-pro-image-preview`

### 403 Permission Denied
- Re-authenticate with correct account
- Set quota project if needed

### Base64 Display Issues
- Ensure `[IMAGE_B64]` regex matches exactly
- Check CLI has `base64` module imported

---

## Success Metrics
✅ Image generation functional  
✅ Global endpoint routing correct  
✅ Authentication configured  
✅ Local file save working  
✅ Clean CLI output  
✅ Nano Banana Pro (Gemini 3) active  

---

**Status:** Production Ready  
**Last Verified:** 2025-12-05 18:52 EST
