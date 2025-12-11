"""Deploy Bandit Agent to Vertex AI Reasoning Engine.

This script packages the Bandit agent logic and deploys it as a remote Reasoning Engine
on Google Cloud Vertex AI.

DAV1D Integration: Includes Google Search grounding, model cost tracking, and enhanced routing.
"""

import os
import argparse
from typing import Optional

import vertexai
from vertexai.preview import reasoning_engines
from langchain_google_vertexai import ChatVertexAI
from langchain_core.messages import SystemMessage, HumanMessage
import requests
from typing import Dict, Any, List

# Hardcoded for now, but could be dynamic
DEFAULT_PROJECT = "project-5f169828-6f8d-450b-923"
DEFAULT_LOCATION = "us-central1"
STAGING_BUCKET = "gs://project-5f169828-6f8d-450b-923-bucket" # Placeholder, user might need to create this

# Model cost tracking (approximate per query based on DAV1D's analysis)
MODEL_COSTS = {
    'lite': 0.0004,       # Gemini 2.5 Flash-Lite
    'flash': 0.0019,      # Gemini 2.5 Flash
    'pro': 0.0075,        # Gemini 2.5 Pro
    'elite': 0.0100,      # Gemini 3.0 Pro
    'image': 0.0400,      # Imagen / Flash Image
    'vision_pro': 0.1340, # Gemini 3 Pro Image
}

# Keywords that trigger Google Search grounding
SEARCH_KEYWORDS = [
    'search', 'google', 'find', 'lookup', 'latest', 'news',
    'current', 'weather', 'price', 'stock', 'today', 'recent',
    'who is', 'what is', 'when did', 'where is', 'breaking',
]

# Load system instructions
def load_system_instruction(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "You are Bandit, the HQ Operator."

class BanditEngine:
    """The Bandit Agent Reasoning Engine with 6-tier intelligent model routing."""

    def __init__(self, project: str, location: str, model: str, system_instruction: str):
        self.project = project
        self.location = location
        self.system_instruction = system_instruction
        
        # Initialize Vertex AI with regional endpoint for 2.5 models
        vertexai.init(project=self.project, location=self.location)
        
        # Initialize Vertex AI generative models
        from vertexai.generative_models import GenerativeModel
        
        # 3-Tier Model System:
        # - flash: gemini-2.5-flash (router + fast responses)
        # - pro: gemini-2.5-pro (coding, analysis, detailed work)
        # - elite: gemini-3-pro-preview (complex reasoning, HIGH tier)
        self.text_models = {
            'lite': ChatVertexAI(model_name="gemini-2.5-flash-lite", temperature=0.7),  # Router
            'flash': ChatVertexAI(model_name="gemini-2.5-flash", temperature=0.7),
            'pro': ChatVertexAI(model_name="gemini-2.5-pro", temperature=0.7),
            # Elite uses global endpoint for Gemini 3
            'elite': ChatVertexAI(
                model_name="gemini-3-pro-preview", 
                temperature=1.0,
                location="global"  # Gemini 3 requires global endpoint
            ),
        }
        
        # Image models (global endpoint only)
        self.image_models = {
            'image': 'gemini-3-pro-image-preview',      # Nano Banana Pro (Gemini 3)
            'flash_image': 'gemini-2.5-flash-image',     # Nano Banana (Flash)
        }

    def set_up(self):
        """Sets up the agent executor (called on the remote worker)."""
        pass
    
    def _select_model_tier(self, prompt: str) -> str:
        """Intelligently select model tier using Flash-Lite as a router.
        
        Uses gemini-2.5-flash-lite to analyze the query and recommend the best tier,
        with keyword-based fallback if routing fails.
        
        Tier Selection Logic:
        - Image (Gemini 3 Pro Image): Image generation/editing ONLY
        - Elite (Gemini 3 Pro): Complex problem solving, multimodal tasks
        - Pro (Gemini 2.5 Pro): Coding, long docs, deep thinking
        - Flash (Gemini 2.5 Flash): High-volume chat, tools, lightweight reasoning
        - Lite (Flash-Lite): Very simple queries
        
        Returns:
            'image', 'lite', 'flash', 'pro', or 'elite'
        """
        prompt_lower = prompt.lower()
        prompt_length = len(prompt)
        
        # Quick check for image generation first (no need to route)
        image_indicators = [
            'generate image', 'create image', 'draw', 'illustrate',
            'make a picture', 'design a', 'generate a visualization',
            'create artwork', 'visual of', 'edit image', 'modify image'
        ]
        if any(indicator in prompt_lower for indicator in image_indicators):
            return 'image'
        
        # Simple greetings/short queries - Flash-Lite handles directly (no routing needed)
        simple_patterns = [
            'hi', 'hey', 'hello', 'yo', 'sup', 'whats up', "what's up",
            'good morning', 'good afternoon', 'good evening', 'gm', 'gn',
            'thanks', 'thank you', 'thx', 'ok', 'okay', 'cool', 'nice',
            'yes', 'no', 'yep', 'nope', 'sure', 'yea', 'yeah'
        ]
        # Very short prompts that match simple patterns go to lite (which is flash-lite)
        if prompt_length < 30 and prompt_lower.strip() in simple_patterns:
            return 'lite'
        
        # Use Flash-Lite as a router model to determine tier
        try:
            router_prompt = f"""Analyze this query and respond with ONLY one word - the recommended model:

QUERY: {prompt[:500]}

Choose based on complexity:
- flash: Simple questions, greetings, quick tasks, general chat
- pro: Coding, analysis, detailed explanations, research
- elite: Complex multi-step problems, strategic planning, deep reasoning

Respond with ONLY: flash, pro, or elite"""

            router_response = self.text_models['lite'].invoke([
                {"role": "user", "content": router_prompt}
            ])
            
            tier = router_response.content.strip().lower()
            # Map any unexpected response to flash
            if tier == 'elite':
                return 'elite'
            elif tier == 'pro':
                return 'pro'
            else:
                return 'flash'  # Default to flash for lite/flash/unknown
        except Exception:
            pass  # Fall through to keyword-based routing
        
        # Fallback: keyword-based routing
        prompt_length = len(prompt)
        
        # IMAGE TIER (Gemini 3 Pro Image) - Image generation/editing ONLY
        # IMAGE TIER (Nano Banana) - Image generation/editing ONLY
        image_indicators = [
            'generate image', 'create image', 'draw', 'illustrate',
            'make a picture', 'design a', 'generate a visualization',
            'create artwork', 'visual of',
            'edit image', 'modify image'
        ]
        
        # Check if prompt explicitly asks for image generation
        if any(indicator in prompt_lower for indicator in image_indicators):
            return 'image'
        
        # ELITE TIER (Gemini 3 Pro) - Complex problem solving, advanced reasoning
        elite_indicators = [
            'complex problem', 'multimodal', 'advanced reasoning',
            'comprehensive analysis', 'strategic planning', 'multi-step solution',
            'synthesize information', 'critical evaluation', 'intricate'
        ]
        
        if any(indicator in prompt_lower for indicator in elite_indicators):
            return 'elite'
        if prompt_length > 600:  # Very long, complex queries
            return 'elite'
        if prompt.count('?') > 4:  # Many interconnected questions
            return 'elite'
        
        # PRO TIER (Gemini 2.5 Pro) - Coding, long context, deep thinking
        pro_indicators = [
            'code', 'function', 'algorithm', 'debug', 'implement',
            'analyze document', 'long context', 'dataset', 'reasoning',
            'think through', 'step by step', 'detailed analysis',
            'compare and contrast', 'evaluate alternatives'
        ]
        
        if any(indicator in prompt_lower for indicator in pro_indicators):
            return 'pro'
        if prompt_length > 300:  # Long queries needing deep thinking
            return 'pro'
        if prompt.count('\n') > 5:  # Multi-paragraph queries
            return 'pro'
        
        # FLASH TIER (Gemini 2.5 Flash) - Chat, tools, lightweight reasoning
        flash_indicators = [
            'explain', 'describe', 'summarize', 'list', 'what is',
            'how to', 'why', 'when', 'where', 'which', 'who',
            'tell me about', 'give me', 'show me'
        ]
        
        if any(indicator in prompt_lower for indicator in flash_indicators):
            return 'flash'
        if prompt_length > 50:  # Standard conversational queries
            return 'flash'
        
        # LITE TIER (Flash-Lite) - Very simple, short queries
        return 'lite'
    
    def _generate_image(self, prompt: str, model_name: str) -> str:
        """Generate an image using Vertex AI GenerativeModel API."""
        from vertexai.generative_models import GenerativeModel
        import vertexai
        
        # Gemini 3 Pro Image is global endpoint only, use 'global' location
        # Gemini 2.5 Flash Image can use regional endpoint
        if 'gemini-3' in model_name:
            vertexai.init(project=self.project, location='global')
        else:
            vertexai.init(project=self.project, location=self.location)
        
        # Use Vertex AI's GenerativeModel for image generation
        model = GenerativeModel(model_name)
        
        # Configure for image output
        generation_config = {
            "temperature": 1.0,  # Gemini 3 default
            "response_modalities": ["IMAGE", "TEXT"],
        }
        
        response = model.generate_content(
            [prompt],
            generation_config=generation_config
        )
        
        # Re-initialize with regional endpoint for subsequent calls
        vertexai.init(project=self.project, location=self.location)
        
        # Extract text and image from response
        result_parts = []
        import base64
        
        for candidate in response.candidates:
            for part in candidate.content.parts:
                # Check for image data FIRST (priority)
                if hasattr(part, 'inline_data') and part.inline_data:
                    # Return base64 for CLI to save locally
                    b64_data = base64.b64encode(part.inline_data.data).decode('utf-8')
                    result_parts.append(f"[IMAGE_B64]{b64_data}[/IMAGE_B64]")
                    result_parts.append(f"✓ Image generated ({len(part.inline_data.data):,} bytes)")
                # Also include any text (thinking/reasoning) 
                elif part.text:
                    result_parts.append(part.text)
        
        return "\n".join(result_parts) if result_parts else "Image generated (no content)."

    def call_external_agent(self, url: str, payload: dict) -> str:
        """Calls another external agent (Reasoning Engine or Cloud Run service).
        
        Use this tool when you need to coordinate with other agents or services.
        
        Args:
            url (str): The full URL of the external agent/service.
            payload (dict): The JSON payload to send.
            
        Returns:
            str: The response from the external agent.
        """
        try:
            # In a real environment, you'd handle auth headers (OIDC) here
            # For now, we assume public or API-key based auth in payload/headers if needed
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            return f"Error calling external agent: {str(e)}"

    def _needs_grounding(self, prompt: str) -> bool:
        """Check if the prompt would benefit from Google Search grounding."""
        prompt_lower = prompt.lower()
        return any(keyword in prompt_lower for keyword in SEARCH_KEYWORDS)
    
    def _query_with_grounding(self, prompt: str) -> str:
        """Query using google.genai with Google Search grounding enabled."""
        from google import genai
        from google.genai.types import GenerateContentConfig, Tool, GoogleSearch, HttpOptions
        
        # Initialize genai client for grounded search
        client = genai.Client(
            vertexai=True,
            project=self.project,
            location=self.location,
            http_options=HttpOptions(api_version="v1")
        )
        
        # Build prompt with system instruction
        full_prompt = f"""{self.system_instruction}

[USER QUERY]
{prompt}

Respond as Bandit. Ground your response in current web data when relevant.
"""
        
        # Configure with Google Search grounding
        config = GenerateContentConfig(
            tools=[Tool(google_search=GoogleSearch())],
            temperature=0.7
        )
        
        response = client.models.generate_content(
            model="gemini-2.5-pro",  # Use Pro for grounded queries
            contents=full_prompt,
            config=config
        )
        
        return response.text if hasattr(response, 'text') else str(response)

    def query(self, prompt: str) -> str:
        """Process a user query with intelligent 6-tier model routing (4 text + 2 image).
        
        Includes:
        - Automatic fallback from elite image model to flash image on 429 errors
        - Google Search grounding for fact-based queries
        """
        # Select optimal model tier
        tier = self._select_model_tier(prompt)
        
        # Handle image generation separately
        if tier == 'image':
            try:
                return self._generate_image(prompt, self.image_models['image'])
            except Exception as e:
                # Handle 429 (rate limit) - fallback to flash image
                if '429' in str(e) or 'quota' in str(e).lower():
                    try:
                        return self._generate_image(prompt, self.image_models['flash_image'])
                    except Exception as fallback_error:
                        # If flash also fails, return error message
                        return f"Image generation failed: {str(e)}"
                else:
                    return f"Image generation error: {str(e)}"
        
        # Check if query needs grounding
        if self._needs_grounding(prompt):
            try:
                return self._query_with_grounding(prompt)
            except Exception as e:
                # Fallback to non-grounded if grounding fails
                pass
        
        # Handle text generation with ChatVertexAI
        model = self.text_models[tier]
        
        messages = [
            SystemMessage(content=self.system_instruction),
            HumanMessage(content=prompt)
        ]
        
        try:
            response = model.invoke(messages)
        except Exception as e:
            raise
        
        # Model selection is transparent to user
        # (tier info only in server logs)
        return response.content

def deploy(args):
    print(f"[deploy] Preparing to deploy Bandit to Reasoning Engine...")
    print(f"- Project: {args.project}")
    print(f"- Location: {args.location}")
    print(f"- Model: {args.model}")
    print(f"- Staging Bucket: {args.staging_bucket}")

    vertexai.init(project=args.project, location=args.location, staging_bucket=args.staging_bucket)

    # Ensure staging bucket exists
    try:
        from google.cloud import storage
        storage_client = storage.Client(project=args.project)
        bucket_name = args.staging_bucket.replace("gs://", "")
        bucket = storage_client.bucket(bucket_name)
        if not bucket.exists():
            print(f"[deploy] Creating staging bucket: {args.staging_bucket}")
            bucket.create(location=args.location)
        else:
            print(f"[deploy] Staging bucket exists: {args.staging_bucket}")
    except Exception as e:
        print(f"[deploy] Warning: Could not verify/create bucket: {e}")

    # Load the actual system instruction to bake into the class
    system_instruction = load_system_instruction(args.system)

    # Create the remote engine
    remote_app = reasoning_engines.ReasoningEngine.create(
        BanditEngine(
            project=args.project,
            location=args.location,
            model=args.model,
            system_instruction=system_instruction
        ),
        requirements=[
            "google-cloud-aiplatform[reasoningengine,langchain]",
            "google-genai",  # For Nano Banana image generation
            "langchain-google-vertexai",
            "langchain-core",
            "google-cloud-storage" # Required for image upload
        ],
        display_name="bandit-agent-hq",
        description="LMSIFY HQ Operator (Bandit)",
    )

    print(f"[deploy] Deployment complete!")
    print(f"- Resource Name: {remote_app.resource_name}")
    return remote_app

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default=DEFAULT_PROJECT)
    parser.add_argument("--location", default=DEFAULT_LOCATION)
    parser.add_argument("--model", default="gemini-3-pro-preview")
    parser.add_argument("--staging-bucket", required=True, help="GCS bucket for staging artifacts (gs://...)")
    parser.add_argument("--system", default="agent-bandit.md")
    
    args = parser.parse_args()
    deploy(args)
