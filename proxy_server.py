import os
import re
import base64
import json
import asyncio
import threading
from collections import OrderedDict
from datetime import datetime
from zoneinfo import ZoneInfo
import uvicorn
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
import google.auth
from google.auth.transport.requests import Request as GoogleRequest
from scripts.bandit_cli import get_engine_resource_name, DEFAULT_PROJECT, DEFAULT_LOCATION, DEFAULT_ENGINE_ID
import requests
import time
from google import genai
from google.genai import types

# Background response cache (LRU-style, max 100 entries)
BACKGROUND_CACHE: OrderedDict = OrderedDict()
CACHE_MAX_SIZE = 100
CACHE_LOCK = threading.Lock()

# Model tiers for different response modes (Gemini 3 Family)
FAST_MODEL = "gemini-3-flash-preview"        # Instant mode - frontier intelligence, 3x faster
FULL_MODEL = "gemini-3-flash-preview"        # Auto mode - balanced (Flash handles most tasks)
DEEP_THINK_MODEL = "gemini-3-pro-preview"    # Deep think - maximum reasoning

# Natural language patterns that trigger deep thinking
DEEP_THINK_PATTERNS = [
    r'\bthink\s*(harder|deeply|more)\b',
    r'\bdeep\s*think\b',
    r'\bultra\s*think\b',
    r'\breason\s*(through|about|deeply)\b',
    r'\banalyze\s*(carefully|deeply|thoroughly)\b',
    r'\btake\s*your\s*time\b',
    r'\bcareful(ly)?\s*consider\b',
]

# God-Level Domain Detection (from 500+ AI Projects Repository)
GOD_LEVEL_DOMAINS = {
    "nlp": {
        "name": "NLP Deity",
        "keywords": ["nlp", "text analysis", "sentiment", "translate", "summarize", "ner", "language model"],
        "boost": "You have mastery of 900+ NLP techniques from the Treasure of Transformers and funNLP repositories."
    },
    "computer_vision": {
        "name": "Vision Omniscience",
        "keywords": ["image", "vision", "detect", "recognize", "camera", "photo", "video", "ocr"],
        "boost": "You have mastery of 1500+ computer vision algorithms from LearnOpenCV and Awesome-CV."
    },
    "deep_learning": {
        "name": "Deep Learning Architect",
        "keywords": ["neural", "train model", "deep learning", "architecture", "tensorflow", "pytorch"],
        "boost": "You have mastery of 2500+ deep learning implementations from TopDeepLearning and DL Drizzle."
    },
    "agents": {
        "name": "Agent Overlord", 
        "keywords": ["multi-agent", "orchestrate", "autonomous", "agent coordination", "chatbot"],
        "boost": "You have mastery of 500+ agent systems from Awesome-Chatbot and Production ML."
    },
    "research": {
        "name": "Research Deity",
        "keywords": ["research", "paper", "sota", "state of the art", "benchmark"],
        "boost": "You have access to state-of-the-art results and latest AI research papers."
    }
}

def detect_god_level_domain(prompt: str) -> dict | None:
    """Detect if prompt requires god-level domain expertise."""
    prompt_lower = prompt.lower()
    for domain_key, domain_info in GOD_LEVEL_DOMAINS.items():
        if any(kw in prompt_lower for kw in domain_info["keywords"]):
            return domain_info
    return None

app = FastAPI(title="Bandit Proxy API", description="OpenAI-compatible proxy for Bandit Reasoning Engine")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup time for uptime tracking
STARTUP_TIME = time.time()
VERSION = "3.1.0"  # Full Gemini 3 Tool Suite Edition

# Pre-initialize genai client at startup to reduce request latency
try:
    from scripts.bandit_cli import DEFAULT_PROJECT
    GENAI_CLIENT = genai.Client(vertexai=True, project=DEFAULT_PROJECT, location="global")
    print(f"[INIT] Pre-initialized genai client for project: {DEFAULT_PROJECT} (global endpoint)")
    print(f"[INIT] God-Level domains loaded: {list(GOD_LEVEL_DOMAINS.keys())}")
except Exception as e:
    GENAI_CLIENT = None
    print(f"[INIT WARNING] Failed to pre-initialize genai client: {e}")

# Auth token cache (tokens valid for ~60 min, refresh at 55 min)
AUTH_TOKEN_CACHE = {"token": None, "expires_at": 0}
AUTH_TOKEN_TTL = 55 * 60  # 55 minutes

# Health Check Endpoint - Visions Fleet Compliant
@app.get("/health")
async def health_check():
    """
    Health check endpoint for Visions Fleet discovery.
    Returns the exact fleet-expected format.
    """
    return {
        "status": "online",
        "agent": "Bandit"
    }

@app.get("/health/detailed")
async def health_detailed():
    """Detailed health check for diagnostics (not fleet-required)."""
    uptime_seconds = int(time.time() - STARTUP_TIME)
    
    auth_status = "unknown"
    try:
        token = get_auth_token()
        auth_status = "ok" if token else "failed"
    except Exception as e:
        auth_status = f"error: {str(e)[:50]}"
    
    return {
        "status": "online",
        "agent": "Bandit",
        "version": VERSION,
        "uptime_seconds": uptime_seconds,
        "auth_status": auth_status,
        "engine_id": DEFAULT_ENGINE_ID,
        "location": DEFAULT_LOCATION,
        "project": DEFAULT_PROJECT,
        "models": {
            "instant": FAST_MODEL,
            "auto": FULL_MODEL,
            "thinking": DEEP_THINK_MODEL
        }
    }

@app.get("/")
async def root():
    """Root endpoint with basic info."""
    return {
        "name": "Bandit Proxy API",
        "version": VERSION,
        "docs": "/docs",
        "health": "/health",
        "cache": "/v1/cache",
        "a2a": "/.well-known/agent.json",
        "rpc": "/rpc"
    }

# ══════════════════════════════════════════════════════════════════════════════
# A2A (Agent-to-Agent) PROTOCOL ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════

# Bandit's advertised skills for A2A discovery
BANDIT_SKILLS = [
    {"name": "chat", "description": "General conversation and Q&A powered by Gemini"},
    {"name": "reasoning", "description": "Deep reasoning via Vertex AI Reasoning Engine"},
    {"name": "multimodal", "description": "Image understanding via Gemini Vision"},
    {"name": "search", "description": "Web-grounded search via Google Search"},
    {"name": "code", "description": "Code generation, explanation, and debugging"},
    {"name": "instant", "description": "Fast responses using gemini-2.5-flash-lite"},
    {"name": "thinking", "description": "Deep thinking mode using gemini-3-pro-preview"},
]

@app.get("/.well-known/agent.json")
async def agent_card(request: Request):
    """
    A2A Agent Card endpoint for discovery.
    Who Visions Fleet standard - allows Leader and peers to discover capabilities.
    """
    return {
        "name": "Bandit",
        "version": VERSION,
        "description": "Advanced reasoning assistant powered by Gemini and Vertex AI Reasoning Engine. Specializes in deep thinking, multimodal understanding, and code generation.",
        "capabilities": [
            "text-generation",
            "code-generation",
            "code-analysis",
            "reasoning",
            "multimodal",
            "web-search"
        ],
        "endpoints": {
            "chat": "/v1/chat/completions",
            "health": "/health"
        },
        "extensions": {
            "color": "bold magenta",
            "role": "Reasoning Engine",
            "models": {
                "instant": FAST_MODEL,
                "auto": FULL_MODEL,
                "thinking": DEEP_THINK_MODEL
            },
            "skills": BANDIT_SKILLS,
            "rpc": "/rpc"
        }
    }

@app.post("/rpc")
async def rpc_endpoint(request: Request):
    """
    A2A JSON-RPC endpoint for agent-to-agent communication.
    
    Supported methods:
    - ask: Send a query to Bandit (uses existing chat logic)
    - list_skills: Get available skills
    - get_status: Get agent status
    """
    import uuid
    
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(
            status_code=400,
            content={"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}, "id": None}
        )
    
    method = body.get("method", "")
    params = body.get("params", {})
    request_id = body.get("id", str(uuid.uuid4()))
    
    # Route to handlers
    if method == "ask":
        result = await a2a_handle_ask(params)
    elif method == "list_skills":
        result = {"skills": BANDIT_SKILLS}
    elif method == "get_status":
        result = {
            "agent": "bandit",
            "version": VERSION,
            "status": "online",
            "uptime_seconds": int(time.time() - STARTUP_TIME),
            "skills_count": len(BANDIT_SKILLS),
            "models": {"instant": FAST_MODEL, "auto": FULL_MODEL, "thinking": DEEP_THINK_MODEL},
            "god_level_domains": list(GOD_LEVEL_DOMAINS.keys())
        }
    else:
        return JSONResponse(
            status_code=400,
            content={
                "jsonrpc": "2.0",
                "error": {"code": -32601, "message": f"Method not found: {method}"},
                "id": request_id
            }
        )
    
    return {"jsonrpc": "2.0", "result": result, "id": request_id}

async def a2a_handle_ask(params: dict) -> dict:
    """Handle A2A 'ask' method by calling the existing chat logic."""
    query = params.get("query", "")
    thinking_mode = params.get("thinking_mode", "instant")
    
    if not query:
        return {"error": "Missing 'query' parameter"}
    
    try:
        # Use the instant path for A2A calls (fast responses)
        client = GENAI_CLIENT or genai.Client(vertexai=True, project=DEFAULT_PROJECT, location="us-central1")
        
        response = client.models.generate_content(
            model=FAST_MODEL if thinking_mode == "instant" else FULL_MODEL,
            contents=query,
            config=types.GenerateContentConfig(
                system_instruction="You are Bandit, an AI assistant. Be helpful and concise.",
                temperature=0.7,
                max_output_tokens=1024,
            )
        )
        
        return {
            "response": response.text,
            "agent": "bandit",
            "model": FAST_MODEL if thinking_mode == "instant" else FULL_MODEL,
            "thinking_mode": thinking_mode
        }
    except Exception as e:
        return {"error": str(e), "agent": "bandit"}

# Import for JSONResponse
from fastapi.responses import JSONResponse

# ══════════════════════════════════════════════════════════════════════════════
# VISIONS FLEET CHAT ENDPOINT
# ══════════════════════════════════════════════════════════════════════════════

class FleetChatRequest(BaseModel):
    """Simple fleet-style chat request with optional tools."""
    message: str
    prompt: Optional[str] = None  # Alias for 'message' (fallback)
    thinking_mode: Optional[str] = "instant"  # Default to fast for fleet calls
    tools: Optional[List[str]] = None  # Optional: ["google_search", "url_context", "code_execution"]

@app.post("/chat")
async def fleet_chat(request: FleetChatRequest):
    """
    Visions Fleet-compatible chat endpoint with optional tools.
    Accepts: {"message": "...", "tools": ["google_search"]}
    Returns: {"response": "..."}
    """
    # Use 'message' or fall back to 'prompt'
    user_message = request.message or request.prompt
    
    if not user_message:
        return JSONResponse(
            status_code=400,
            content={"error": "Missing 'message' or 'prompt' field"}
        )
    
    thinking_mode = request.thinking_mode or "instant"
    
    try:
        # Use the fast path for fleet calls (low latency)
        client = GENAI_CLIENT or genai.Client(vertexai=True, project=DEFAULT_PROJECT, location="global")
        
        # Select model and thinking_level based on thinking mode (Gemini 3 API)
        if thinking_mode == "thinking":
            model = DEEP_THINK_MODEL
            sys_prompt = "You are Bandit, an advanced AI with deep reasoning. Take time to think through problems."
            max_tokens = 4096
            thinking_level = "high"  # Maximum reasoning depth
        elif thinking_mode == "auto":
            model = FULL_MODEL
            sys_prompt = "You are Bandit, a helpful AI assistant."
            max_tokens = 2048
            thinking_level = "medium"  # Balanced thinking (Flash only)
        else:  # instant
            model = FAST_MODEL
            sys_prompt = "You are Bandit, a fast AI assistant. Be concise."
            max_tokens = 1024
            thinking_level = "low"  # Minimize latency
        
        # Build tools list from request
        active_tools = []
        if request.tools:
            for tool_name in request.tools:
                if tool_name == "google_search":
                    active_tools.append(types.Tool(google_search=types.GoogleSearch()))
                elif tool_name == "url_context":
                    active_tools.append(types.Tool(url_context=types.UrlContext()))
                elif tool_name == "code_execution":
                    active_tools.append(types.Tool(code_execution=types.ToolCodeExecution))
        
        response = client.models.generate_content(
            model=model,
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=sys_prompt,
                temperature=1.0,  # Gemini 3 recommended - avoid looping issues
                max_output_tokens=max_tokens,
                thinking_config=types.ThinkingConfig(thinking_level=thinking_level),
                tools=active_tools if active_tools else None,
            )
        )
        
        result = {
            "response": response.text,
            "agent": "Bandit",
            "model": model,
            "thinking_mode": thinking_mode
        }
        
        # Add tool-specific metadata if tools were used
        if request.tools:
            result["tools_used"] = request.tools
            # Add grounding metadata if available
            if response.candidates and response.candidates[0].grounding_metadata:
                result["grounding_metadata"] = True
        
        return result
        
    except Exception as e:
        print(f"[FLEET CHAT ERROR] {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "agent": "Bandit"}
        )

@app.post("/generate")
async def fleet_generate(request: FleetChatRequest):
    """
    KRONOS Fleet-compatible generate endpoint.
    Alias for /chat - matches KRONOS's POST /generate spec.
    """
    return await fleet_chat(request)

# ══════════════════════════════════════════════════════════════════════════════
# GEMINI 3 TOOL ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════

# Request Models for Tool Endpoints
class SearchRequest(BaseModel):
    """Google Search grounding request."""
    query: str
    thinking_mode: Optional[str] = "instant"

class UrlRequest(BaseModel):
    """URL Context analysis request."""
    prompt: str
    urls: List[str]
    
class CodeRequest(BaseModel):
    """Code Execution request."""
    prompt: str
    
class ResearchRequest(BaseModel):
    """Deep Research async request."""
    topic: str
    format: Optional[str] = None  # Optional formatting instructions

# ─────────────────────────────────────────────────────────────────────────────
# GOOGLE SEARCH GROUNDING
# ─────────────────────────────────────────────────────────────────────────────

@app.post("/search")
async def search_grounded(request: SearchRequest):
    """
    Grounded response using Google Search.
    Returns real-time web search results with citations.
    """
    try:
        client = GENAI_CLIENT or genai.Client(vertexai=True, project=DEFAULT_PROJECT, location="global")
        
        response = client.models.generate_content(
            model=FAST_MODEL,
            contents=request.query,
            config=types.GenerateContentConfig(
                system_instruction="You are Bandit, an AI with real-time web access. Provide accurate, grounded responses.",
                temperature=1.0,
                tools=[types.Tool(google_search=types.GoogleSearch())],
                thinking_config=types.ThinkingConfig(thinking_level="low" if request.thinking_mode == "instant" else "medium"),
            )
        )
        
        # Extract grounding metadata
        grounding_metadata = None
        if response.candidates and response.candidates[0].grounding_metadata:
            gm = response.candidates[0].grounding_metadata
            grounding_metadata = {
                "web_search_queries": gm.web_search_queries if hasattr(gm, 'web_search_queries') else [],
                "grounding_chunks": [{"uri": c.web.uri, "title": c.web.title} for c in (gm.grounding_chunks or [])] if hasattr(gm, 'grounding_chunks') else [],
            }
        
        return {
            "response": response.text,
            "agent": "Bandit",
            "model": FAST_MODEL,
            "tool": "google_search",
            "grounding_metadata": grounding_metadata
        }
        
    except Exception as e:
        print(f"[SEARCH ERROR] {e}")
        return JSONResponse(status_code=500, content={"error": str(e), "agent": "Bandit"})

# ─────────────────────────────────────────────────────────────────────────────
# URL CONTEXT ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────

@app.post("/analyze-url")
async def analyze_url(request: UrlRequest):
    """
    Analyze content from URLs.
    Fetches and processes web page content to answer questions.
    """
    try:
        client = GENAI_CLIENT or genai.Client(vertexai=True, project=DEFAULT_PROJECT, location="global")
        
        # Build prompt with URLs
        url_list = "\n".join([f"- {url}" for url in request.urls])
        full_prompt = f"{request.prompt}\n\nAnalyze the following URLs:\n{url_list}"
        
        response = client.models.generate_content(
            model=FAST_MODEL,
            contents=full_prompt,
            config=types.GenerateContentConfig(
                system_instruction="You are Bandit, analyzing web content. Extract and synthesize information from the provided URLs.",
                temperature=1.0,
                tools=[types.Tool(url_context=types.UrlContext())],
            )
        )
        
        # Extract URL metadata
        url_metadata = None
        if response.candidates and hasattr(response.candidates[0], 'url_context_metadata'):
            ucm = response.candidates[0].url_context_metadata
            if ucm and hasattr(ucm, 'url_metadata'):
                url_metadata = [{"url": m.retrieved_url, "status": m.url_retrieval_status} for m in ucm.url_metadata]
        
        return {
            "response": response.text,
            "agent": "Bandit",
            "model": FAST_MODEL,
            "tool": "url_context",
            "url_metadata": url_metadata
        }
        
    except Exception as e:
        print(f"[URL CONTEXT ERROR] {e}")
        return JSONResponse(status_code=500, content={"error": str(e), "agent": "Bandit"})

# ─────────────────────────────────────────────────────────────────────────────
# CODE EXECUTION
# ─────────────────────────────────────────────────────────────────────────────

@app.post("/execute-code")
async def execute_code(request: CodeRequest):
    """
    Execute Python code using Gemini's sandbox.
    The model generates and runs code, returning results.
    """
    try:
        client = GENAI_CLIENT or genai.Client(vertexai=True, project=DEFAULT_PROJECT, location="global")
        
        response = client.models.generate_content(
            model=FAST_MODEL,
            contents=request.prompt,
            config=types.GenerateContentConfig(
                system_instruction="You are Bandit, a coding assistant. Generate and execute Python code to solve problems.",
                temperature=1.0,
                tools=[types.Tool(code_execution=types.ToolCodeExecution)],
            )
        )
        
        # Extract code parts from response
        code_parts = []
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'executable_code') and part.executable_code:
                    code_parts.append({
                        "type": "code",
                        "language": part.executable_code.language if hasattr(part.executable_code, 'language') else "PYTHON",
                        "content": part.executable_code.code
                    })
                elif hasattr(part, 'code_execution_result') and part.code_execution_result:
                    code_parts.append({
                        "type": "result",
                        "outcome": part.code_execution_result.outcome if hasattr(part.code_execution_result, 'outcome') else "OK",
                        "content": part.code_execution_result.output
                    })
                elif hasattr(part, 'text') and part.text:
                    code_parts.append({
                        "type": "text",
                        "content": part.text
                    })
        
        return {
            "response": response.text,
            "agent": "Bandit",
            "model": FAST_MODEL,
            "tool": "code_execution",
            "code_parts": code_parts
        }
        
    except Exception as e:
        print(f"[CODE EXECUTION ERROR] {e}")
        return JSONResponse(status_code=500, content={"error": str(e), "agent": "Bandit"})

# ─────────────────────────────────────────────────────────────────────────────
# DEEP RESEARCH AGENT (ASYNC)
# ─────────────────────────────────────────────────────────────────────────────

DEEP_RESEARCH_AGENT = "deep-research-pro-preview-12-2025"

@app.post("/research")
async def deep_research(request: ResearchRequest):
    """
    Start async deep research task.
    Returns interaction_id to poll for results.
    """
    try:
        client = GENAI_CLIENT or genai.Client(vertexai=True, project=DEFAULT_PROJECT, location="global")
        
        # Build research prompt with optional formatting
        research_prompt = request.topic
        if request.format:
            research_prompt += f"\n\nFormat the output as follows:\n{request.format}"
        
        interaction = client.interactions.create(
            input=research_prompt,
            agent=DEEP_RESEARCH_AGENT,
            background=True,
            agent_config={
                "type": "deep-research",
                "thinking_summaries": "auto"
            }
        )
        
        return {
            "interaction_id": interaction.id,
            "status": "started",
            "agent": "Bandit",
            "research_agent": DEEP_RESEARCH_AGENT,
            "message": "Deep research started. Poll /research/{interaction_id} for results."
        }
        
    except Exception as e:
        print(f"[DEEP RESEARCH ERROR] {e}")
        return JSONResponse(status_code=500, content={"error": str(e), "agent": "Bandit"})

@app.get("/research/{interaction_id}")
async def get_research_status(interaction_id: str):
    """
    Poll research task status.
    Returns completed report when done.
    """
    try:
        client = GENAI_CLIENT or genai.Client(vertexai=True, project=DEFAULT_PROJECT, location="global")
        
        interaction = client.interactions.get(interaction_id)
        
        if interaction.status == "completed":
            return {
                "status": "completed",
                "report": interaction.outputs[-1].text if interaction.outputs else None,
                "agent": "Bandit"
            }
        elif interaction.status == "failed":
            return {
                "status": "failed",
                "error": str(interaction.error) if hasattr(interaction, 'error') else "Unknown error",
                "agent": "Bandit"
            }
        else:
            return {
                "status": "in_progress",
                "agent": "Bandit",
                "message": "Research still in progress. Poll again in 10 seconds."
            }
        
    except Exception as e:
        print(f"[RESEARCH STATUS ERROR] {e}")
        return JSONResponse(status_code=500, content={"error": str(e), "agent": "Bandit"})

@app.get("/v1/cache")
async def get_cached_response(prompt: str = ""):
    """Retrieve a cached background response if available."""
    if not prompt:
        return {"cached": False, "cache_size": len(BACKGROUND_CACHE)}
    
    key = cache_key(prompt)
    cached = cache_get(key)
    
    if cached:
        return {
            "cached": True,
            "response": cached,
            "model": "bandit-reasoning-engine",
            "key": key[:8]
        }
    
    return {"cached": False, "key": key[:8]}

# Models
class Message(BaseModel):
    role: str
    content: Union[str, List[Dict[str, Any]]]
    name: Optional[str] = None

class ChatCompletionRequest(BaseModel):
    model: str = "bandit-v1.0"
    messages: List[Message]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    stream: bool = False
    thinking_mode: Optional[str] = "auto"  # 'instant' = flash-lite bypass, 'thinking' = full reasoning, 'auto' = adaptive

class Choice(BaseModel):
    index: int
    message: Message
    finish_reason: str

class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[Choice]
    usage: Dict[str, int]

# Deep thinking detection
def detect_deep_thinking(prompt: str) -> bool:
    """Detect if the user's prompt requests deep thinking/reasoning."""
    prompt_lower = prompt.lower()
    for pattern in DEEP_THINK_PATTERNS:
        if re.search(pattern, prompt_lower, re.IGNORECASE):
            return True
    return False

def cache_key(prompt: str) -> str:
    """Generate a cache key from prompt."""
    import hashlib
    return hashlib.md5(prompt.encode()).hexdigest()[:16]

def cache_set(key: str, value: str):
    """Store a value in the background cache."""
    with CACHE_LOCK:
        if key in BACKGROUND_CACHE:
            BACKGROUND_CACHE.move_to_end(key)
        BACKGROUND_CACHE[key] = {"response": value, "timestamp": time.time()}
        while len(BACKGROUND_CACHE) > CACHE_MAX_SIZE:
            BACKGROUND_CACHE.popitem(last=False)

def cache_get(key: str) -> Optional[str]:
    """Retrieve a value from the background cache."""
    with CACHE_LOCK:
        if key in BACKGROUND_CACHE:
            BACKGROUND_CACHE.move_to_end(key)
            return BACKGROUND_CACHE[key]["response"]
        return None

def background_reasoning_query(prompt: str, cache_key_str: str):
    """Run a background query to the Reasoning Engine and cache the result."""
    try:
        print(f"[BACKGROUND] Starting Reasoning Engine query for key: {cache_key_str[:8]}...")
        start = time.time()
        
        token = get_auth_token()
        if not token:
            print("[BACKGROUND] Failed to get auth token")
            return
        
        resource_name = get_engine_resource_name(DEFAULT_PROJECT, DEFAULT_LOCATION, DEFAULT_ENGINE_ID)
        api_endpoint = f"https://{DEFAULT_LOCATION}-aiplatform.googleapis.com/v1beta1/{resource_name}:query"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "input": {"prompt": prompt},
            "classMethod": "query"
        }
        
        response = requests.post(api_endpoint, headers=headers, json=payload, timeout=120)
        
        if response.status_code == 200:
            result_json = response.json()
            bandit_response = result_json.get("output", "")
            if isinstance(bandit_response, dict):
                bandit_response = str(bandit_response)
            
            cache_set(cache_key_str, bandit_response)
            elapsed = time.time() - start
            print(f"[BACKGROUND] Cached response in {elapsed:.2f}s for key: {cache_key_str[:8]}")
        else:
            print(f"[BACKGROUND] Error: {response.status_code}")
            
    except Exception as e:
        print(f"[BACKGROUND ERROR] {e}")

# Auth Helper with caching
def get_auth_token():
    """Get authentication token for GCP API calls. Uses cache to avoid latency spikes."""
    global AUTH_TOKEN_CACHE
    
    # Check cache first
    now = time.time()
    if AUTH_TOKEN_CACHE["token"] and AUTH_TOKEN_CACHE["expires_at"] > now:
        return AUTH_TOKEN_CACHE["token"]  # Return cached token (silent - no print)
    
    try:
        credentials, project = google.auth.default()
        
        if not credentials.valid or credentials.expired:
            credentials.refresh(GoogleRequest())
        
        token = credentials.token
        if token:
            AUTH_TOKEN_CACHE["token"] = token
            AUTH_TOKEN_CACHE["expires_at"] = now + AUTH_TOKEN_TTL
            print(f"[AUTH] Token refreshed and cached for {AUTH_TOKEN_TTL//60} min")
            return token
            
    except Exception as e:
        print(f"[AUTH ERROR] {e}")
        # Fallback to gcloud
        try:
            import subprocess
            result = subprocess.run(
                ["gcloud", "auth", "print-access-token"],
                capture_output=True, text=True, shell=True, timeout=10
            )
            if result.returncode == 0:
                token = result.stdout.strip().split('\n')[-1]
                if token.startswith('ya29.'):
                    AUTH_TOKEN_CACHE["token"] = token
                    AUTH_TOKEN_CACHE["expires_at"] = now + AUTH_TOKEN_TTL
                    print(f"[AUTH] Token from gcloud, cached for {AUTH_TOKEN_TTL//60} min")
                    return token
        except Exception as e2:
            print(f"[AUTH ERROR] Fallback failed: {e2}")
    
    return None

def parse_gemini_content(content: Union[str, List[Dict[str, Any]]]) -> tuple[str, Any]:
    """
    Parse OpenAI-style content into (text_prompt, gemini_contents).
    Returns:
        text_prompt: A string representation for logging/reasoning-engine fallback.
        gemini_contents: A format suitable for client.models.generate_content.
    """
    if isinstance(content, str):
        return content, content
    
    # Handle list of parts (Multimodal)
    text_parts = []
    gemini_parts = []
    
    for part in content:
        if part.get("type") == "text":
            text_val = part.get("text", "")
            text_parts.append(text_val)
            gemini_parts.append(types.Part.from_text(text=text_val))
            
        elif part.get("type") == "image_url":
            image_url = part.get("image_url", {}).get("url", "")
            # Expecting data:image/jpeg;base64,.....
            if image_url.startswith("data:"):
                try:
                    header, encoded = image_url.split(",", 1)
                    mime_type = header.split(":")[1].split(";")[0]
                    data = base64.b64decode(encoded)
                    gemini_parts.append(types.Part.from_bytes(data=data, mime_type=mime_type))
                    text_parts.append("[Image]")
                except Exception as e:
                    print(f"[IMAGE ERROR] Failed to decode base64: {e}")
            else:
                # Handle standard URLs if needed, but for now just log it
                text_parts.append(f"[Image URL: {image_url}]")

    prompt_text = "\n".join(text_parts)
    return prompt_text, gemini_parts

# Proxy Endpoint
@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
async def chat_completions(request: ChatCompletionRequest):
    start_time = time.time()
    
    # Extract Prompt
    last_user_msg = next((m for m in reversed(request.messages) if m.role == "user"), None)
    if not last_user_msg:
        raise HTTPException(status_code=400, detail="No user message found")
    
    original_prompt, gemini_contents = parse_gemini_content(last_user_msg.content)
    
    # Skip time injection for instant mode (reduces latency)
    if request.thinking_mode == "instant":
        prompt = original_prompt
    else:
        ny_time = datetime.now(ZoneInfo("America/New_York")).strftime("%Y-%m-%d %H:%M:%S %Z")
        prompt = f"[Current Time: {ny_time}]\n{original_prompt}"
        # Update gemini_contents if it's just a string, otherwise prepend time? 
        # For simplicity, if multimodal, we keep gemini_contents as Parts and just rely on the model.
        # If string, we update it.
        if isinstance(gemini_contents, str):
            gemini_contents = prompt
        # TODO: Handle multimodal time injection cleanly if needed, but usually image queries are direct.
    
    thinking_mode = request.thinking_mode or "auto"
    bandit_response = ""
    model_used = ""
    
    # Check for natural language deep thinking triggers in auto mode
    if thinking_mode == "auto" and detect_deep_thinking(original_prompt):
        print(f"[AUTO] Detected deep thinking request in prompt, upgrading to 'thinking' mode")
        thinking_mode = "thinking"
    
    # FAST PATH: Use gemini-3-flash-preview directly (bypasses Reasoning Engine routing)
    if thinking_mode == "instant":
        try:
            print(f"[FAST PATH] Using {FAST_MODEL}...")
            client = GENAI_CLIENT or genai.Client(vertexai=True, project=DEFAULT_PROJECT, location="us-central1")
            
            response = client.models.generate_content(
                model=FAST_MODEL,
                contents=gemini_contents,
                config=types.GenerateContentConfig(
                    system_instruction="You are Bandit, a fast AI assistant. Be concise.",
                    temperature=1.0,  # Gemini 3 recommended
                    max_output_tokens=1024,
                    thinking_config=types.ThinkingConfig(thinking_level="low"),
                )
            )
            
            bandit_response = response.text
            model_used = FAST_MODEL
            elapsed = time.time() - start_time
            print(f"[FAST PATH] Completed in {elapsed:.2f}s")
            
            # Fire background query to Reasoning Engine for richer response
            key = cache_key(prompt)
            if not cache_get(key):  # Only if not already cached
                bg_thread = threading.Thread(
                    target=background_reasoning_query,
                    args=(prompt, key),
                    daemon=True
                )
                bg_thread.start()
                print(f"[FAST PATH] Spawned background query thread")
            
        except Exception as e:
            print(f"[FAST PATH ERROR] {e}, falling back...")
            thinking_mode = "auto"  # Fall back to full path
    
    # DEEP THINK PATH: Use gemini-3-pro-preview for maximum reasoning
    if thinking_mode == "thinking" and not bandit_response:
        try:
            print(f"[DEEP THINK] Using {DEEP_THINK_MODEL} for deep reasoning...")
            client = genai.Client(vertexai=True, project=DEFAULT_PROJECT, location="us-central1")
            
            # System instruction for deep thinking mode
            system_instruction = """You are Bandit, an advanced AI assistant with deep reasoning capabilities.
Take your time to think through problems carefully and thoroughly.
Provide detailed, well-reasoned responses. You're in deep thinking mode."""
            
            response = client.models.generate_content(
                model=DEEP_THINK_MODEL,
                contents=gemini_contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=1.0,  # Gemini 3 recommended
                    max_output_tokens=8192,
                    thinking_config=types.ThinkingConfig(thinking_level="high"),
                )
            )
            
            bandit_response = response.text
            model_used = DEEP_THINK_MODEL
            elapsed = time.time() - start_time
            print(f"[DEEP THINK] Completed in {elapsed:.2f}s")
            
        except Exception as e:
            print(f"[DEEP THINK ERROR] {e}, falling back to Reasoning Engine...")
            thinking_mode = "auto"  # Fall back to full path
    
    # FULL PATH: Use Reasoning Engine (for 'thinking' and 'auto' modes, or fallback)
    if not bandit_response:
        # Get Authentication
        token = get_auth_token()
        if not token:
            raise HTTPException(status_code=500, detail="Failed to get authentication token")
        
        resource_name = get_engine_resource_name(DEFAULT_PROJECT, DEFAULT_LOCATION, DEFAULT_ENGINE_ID)
        api_endpoint = f"https://{DEFAULT_LOCATION}-aiplatform.googleapis.com/v1beta1/{resource_name}:query"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "input": {"prompt": prompt},
            "classMethod": "query"
        }
        
        try:
            print(f"[FULL PATH] Using Reasoning Engine...")
            response = requests.post(api_endpoint, headers=headers, json=payload, timeout=120)
            
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=f"Bandit Error: {response.text}")
            
            result_json = response.json()
            bandit_response = result_json.get("output", "")
            if isinstance(bandit_response, dict):
                bandit_response = str(bandit_response)
            model_used = "bandit-reasoning-engine"
            elapsed = time.time() - start_time
            print(f"[FULL PATH] Completed in {elapsed:.2f}s")
                
        except requests.exceptions.Timeout:
            raise HTTPException(status_code=504, detail="Bandit Request Timed Out")
        except Exception as e:
            print(f"Proxy Error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
        
    # Format OpenAI Response
    return ChatCompletionResponse(
        id=f"chatcmpl-{int(time.time())}",
        created=int(time.time()),
        model=model_used or request.model,
        choices=[
            Choice(
                index=0,
                message=Message(role="assistant", content=bandit_response),
                finish_reason="stop"
            )
        ],
        usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
