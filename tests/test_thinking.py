
import os
import asyncio
from google import genai
from google.genai import types

async def probe_thinking():
    print("[*] Init Client...")
    # Auto-detect project like before
    import google.auth
    try:
        _, PROJECT_ID = google.auth.default()
        client = genai.Client(vertexai=True, project=PROJECT_ID, location="us-central1")
    except:
        client = genai.Client(vertexai=True, location="us-central1")

    model = "gemini-2.5-flash"
    
    print(f"[*] Sending request to {model}...")
    try:
        # Chat with streaming
        chat = client.aio.chats.create(
            model=model,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(
                    include_thoughts=True,
                    thinking_budget=1024  # Low thinking for speed
                ) 
            )
        )
        
        print("\n--- STREAM START ---")
        # Fix: await the stream method if it is a coroutine
        response_stream = await chat.send_message_stream("Why is the sky blue? Explain concisely.")
        async for chunk in response_stream:
            # Inspect chunk structure
            # In new SDK, thoughts might be in separate part or field
            if hasattr(chunk, 'candidates') and chunk.candidates:
                for cand in chunk.candidates:
                    if hasattr(cand, 'content') and cand.content:
                        for part in cand.content.parts:
                            if hasattr(part, 'thought') and part.thought:
                                print(f"[Thinking] {part.thought[:50]}...")
                            if hasattr(part, 'text') and part.text:
                                print(f"[Text] {part.text}")
                                
        print("--- STREAM END ---")
        
    except Exception as e:
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    asyncio.run(probe_thinking())
