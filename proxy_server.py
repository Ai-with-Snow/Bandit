import os
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
import google.auth
from google.auth.transport.requests import Request as GoogleRequest
from scripts.bandit_cli import get_engine_resource_name, DEFAULT_PROJECT, DEFAULT_LOCATION, DEFAULT_ENGINE_ID
import requests
import time

app = FastAPI(title="Bandit Proxy API", description="OpenAI-compatible proxy for Bandit Reasoning Engine")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class Message(BaseModel):
    role: str
    content: str
    name: Optional[str] = None

class ChatCompletionRequest(BaseModel):
    model: str = "bandit-v1.0"
    messages: List[Message]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    stream: bool = False

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

# Auth Helper
def get_auth_token():
    credentials, project = google.auth.default()
    if not credentials.valid:
        if credentials.expired and credentials.refresh_token:
            credentials.refresh(GoogleRequest())
        else:
            # Fallback for local dev if default credentials aren't fully set up
            try:
                import subprocess
                result = subprocess.run(
                    ["gcloud", "auth", "print-access-token"],
                    capture_output=True, text=True, check=True, shell=True
                )
                return result.stdout.strip()
            except Exception as e:
                print(f"Auth Error: {e}")
                return None
    return credentials.token

# Proxy Endpoint
@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
async def chat_completions(request: ChatCompletionRequest):
    start_time = time.time()
    
    # 1. Get Authentication
    token = get_auth_token()
    if not token:
        raise HTTPException(status_code=500, detail="Failed to get authentication token")
    
    # 2. Extract Prompt (Last user message for simplicity, or full context)
    # Bandit accepts a 'prompt' string. We'll concatenate recent history or just take the last msg.
    # Ideally, Bandit's MemoryManager handles history, so we just send the NEW user input.
    last_user_msg = next((m for m in reversed(request.messages) if m.role == "user"), None)
    if not last_user_msg:
        raise HTTPException(status_code=400, detail="No user message found")
    
    prompt = last_user_msg.content
    
    # 3. Call Bandit Reasoning Engine
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
        response = requests.post(api_endpoint, headers=headers, json=payload, timeout=120)
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=f"Bandit Error: {response.text}")
        
        result_json = response.json()
        bandit_response = result_json.get("output", "")
        # Fallback if output structure varies
        if isinstance(bandit_response, dict):
             bandit_response = str(bandit_response)
        
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Bandit Request Timed Out")
    except Exception as e:
        print(f"Proxy Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
        
    # 4. Format OpenAI Response
    return ChatCompletionResponse(
        id=f"chatcmpl-{int(time.time())}",
        created=int(time.time()),
        model=request.model,
        choices=[
            Choice(
                index=0,
                message=Message(role="assistant", content=bandit_response),
                finish_reason="stop"
            )
        ],
        usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0} # Placeholder
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
