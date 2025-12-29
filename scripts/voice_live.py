#!/usr/bin/env python3
"""
Bandit Live API Mode - Full Duplex Streaming Voice
Uses Gemini Live 2.5 Flash for real-time bidirectional conversation.

Features:
- Real-time audio streaming (no wait for full response)
- Native barge-in (interrupt naturally)
- Automatic turn-taking
- Built-in audio I/O handling

Usage:
    python scripts/voice_live.py
    python scripts/voice_live.py --voice Charon
"""

import os
import asyncio
import argparse
import pyaudio
import numpy as np
import warnings
from google import genai
from google.genai import types

# Suppress deprecation warnings for cleaner output
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Live API Model
LIVE_MODEL = "gemini-live-2.5-flash"
BANDIT_VOICE = "Charon"  # Default voice

BANDIT_LIVE_PROMPT = """YOU ARE BANDIT. An AI assistant created by LMSIFY.

[PERSONA]
- Helpful, knowledgeable, and slightly playful
- Direct and efficient - don't waste words
- Friendly but professional
- Part of the Snowverse ecosystem

[LIVE MODE]
- Real-time bidirectional voice conversation
- Brief, natural responses (1-3 sentences for casual chat)
- Use turn-taking cues to know when to respond
- Can be interrupted naturally
- Remember conversation context automatically

[CAPABILITIES]
- Answer questions using your knowledge
- Help with coding and technical tasks
- Discuss LMSIFY brands: Irie Igloo, Velvet Hours, Merpz, BLVDMND

Keep it natural. Keep it real. You got this.
"""


class AudioHandler:
    """Handles audio input/output for Live API."""
    
    def __init__(self, input_sample_rate: int = 16000, output_sample_rate: int = 24000):
        self.input_rate = input_sample_rate
        self.output_rate = output_sample_rate
        self.chunk_size = 1024
        self.pa = pyaudio.PyAudio()
        
        # Find default devices
        self.input_device = self.pa.get_default_input_device_info()['index']
        self.output_device = self.pa.get_default_output_device_info()['index']
        
        self._input_stream = None
        self._output_stream = None
        self._running = False
    
    def start_input(self):
        """Start audio input stream."""
        self._input_stream = self.pa.open(
            format=self.pa.get_format_from_width(2),
            channels=1,
            rate=self.input_rate,
            input=True,
            input_device_index=self.input_device,
            frames_per_buffer=self.chunk_size
        )
        self._running = True
    
    def start_output(self):
        """Start audio output stream."""
        self._output_stream = self.pa.open(
            format=self.pa.get_format_from_width(2),
            channels=1,
            rate=self.output_rate,
            output=True,
            output_device_index=self.output_device,
            frames_per_buffer=self.chunk_size
        )
    
    async def capture_audio(self):
        """Generator that yields audio chunks from microphone."""
        while self._running:
            try:
                data = self._input_stream.read(self.chunk_size, exception_on_overflow=False)
                yield data
            except Exception:
                await asyncio.sleep(0.01)
    
    def play_audio(self, audio_data: bytes):
        """Play audio through speakers."""
        if self._output_stream:
            self._output_stream.write(audio_data)
    
    def stop(self):
        """Stop all streams."""
        self._running = False
        if self._input_stream:
            self._input_stream.stop_stream()
            self._input_stream.close()
        if self._output_stream:
            self._output_stream.stop_stream()
            self._output_stream.close()
        self.pa.terminate()


def initialize_client() -> genai.Client:
    """Initialize Gemini client."""
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    
    if api_key:
        print("[*] Using API key authentication")
        return genai.Client(api_key=api_key)
    
    project = os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("GCP_PROJECT")
    if project:
        print(f"[*] Using Vertex AI (project: {project})")
        return genai.Client(vertexai=True, project=project, location="global")
    
    print("[*] Using Vertex AI with default credentials")
    return genai.Client(vertexai=True, location="global")


async def live_mode(voice: str = BANDIT_VOICE):
    """Bandit with Gemini Live API - Full duplex streaming."""
    
    print("\n" + "="*60)
    print("🎙️  BANDIT LIVE API MODE - NATIVE STREAMING")
    print("="*60)
    print(f"  Model:    {LIVE_MODEL}")
    print(f"  Voice:    {voice}")
    print(f"  Barge-in: Enabled (interrupt naturally)")
    print(f"  Memory:   Automatic context")
    print("="*60 + "\n")
    
    client = initialize_client()
    audio = AudioHandler()
    
    # Live API configuration
    config = types.LiveConnectConfig(
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                    voice_name=voice
                )
            )
        ),
        system_instruction=types.Content(
            parts=[types.Part(text=BANDIT_LIVE_PROMPT)]
        )
    )
    
    try:
        # Connect to Live API
        async with client.aio.live.connect(
            model=LIVE_MODEL,
            config=config
        ) as session:
            
            print("[✓] Connected to Gemini Live API")
            print("[*] Start speaking... (Ctrl+C to exit)\n")
            
            # Start audio handlers
            audio.start_input()
            audio.start_output()
            
            # Create tasks for send and receive
            async def send_audio():
                """Send microphone audio to Live API."""
                async for chunk in audio.capture_audio():
                    try:
                        await session.send(
                            input=types.LiveClientRealtimeInput(
                                media_chunks=[
                                    types.Blob(
                                        mime_type="audio/pcm",
                                        data=chunk
                                    )
                                ]
                            ),
                            end_of_turn=False
                        )
                    except Exception as e:
                        print(f"[Send Error] {e}")
                        break
            
            async def receive_audio():
                """Receive and play audio from Live API."""
                async for response in session.receive():
                    try:
                        # Handle different response types
                        if hasattr(response, 'data') and response.data:
                            # Audio data
                            audio.play_audio(response.data)
                        
                        if hasattr(response, 'server_content'):
                            content = response.server_content
                            
                            # Check for audio parts
                            if hasattr(content, 'model_turn') and content.model_turn:
                                for part in content.model_turn.parts:
                                    if hasattr(part, 'inline_data') and part.inline_data:
                                        audio.play_audio(part.inline_data.data)
                            
                            # Check for turn complete
                            if hasattr(content, 'turn_complete') and content.turn_complete:
                                print("[Turn complete]")
                        
                        # Handle interruption
                        if hasattr(response, 'server_content'):
                            if hasattr(response.server_content, 'interrupted') and response.server_content.interrupted:
                                print("[Interrupted]")
                                
                    except Exception as e:
                        print(f"[Receive Error] {e}")
                        break
            
            # Run both tasks concurrently
            send_task = asyncio.create_task(send_audio())
            receive_task = asyncio.create_task(receive_audio())
            
            try:
                await asyncio.gather(send_task, receive_task)
            except asyncio.CancelledError:
                pass
            
    except KeyboardInterrupt:
        print("\n[*] Disconnecting from Live API...")
    except Exception as e:
        print(f"[!] Error: {e}")
    finally:
        audio.stop()
        print("[*] Goodbye! 👋")


async def main():
    parser = argparse.ArgumentParser(description="Bandit Live API Mode")
    parser.add_argument("--voice", default=BANDIT_VOICE, 
                        help=f"TTS voice name (default: {BANDIT_VOICE})")
    parser.add_argument("--list-voices", action="store_true",
                        help="List available voices")
    args = parser.parse_args()
    
    if args.list_voices:
        print("\n🎙️ Available Voices:\n")
        print("Female: Zephyr, Kore, Leda, Aoede, Callirrhoe, Autonoe,")
        print("        Erinome, Laomedeia, Pulcherrima, Vindemiatrix,")
        print("        Achernar, Despina, Gacrux, Sulafat")
        print("\nMale:   Puck, Charon, Fenrir, Orus, Enceladus, Iapetus,")
        print("        Umbriel, Algieba, Algenib, Rasalgethi, Alnilam,")
        print("        Schedar, Achird, Zubenelgenubi, Sadachbia, Sadaltager")
        print()
        return
    
    await live_mode(args.voice)


if __name__ == "__main__":
    asyncio.run(main())
