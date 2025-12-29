#!/usr/bin/env python3
"""
Bandit Hi-Fi Voice Engine (Chirp 3 HD)
Uses Google Cloud Speech-to-Text v2 (Chirp) and Text-to-Speech v1 (Chirp HD).

Features:
- High-fidelity TTS (Chirp 3 HD voices)
- High-accuracy STT (Chirp Universal Speech Model)
- Rich dashboard and session management
- Fallback to standard models if Chirp unavailable

Usage:
    python scripts/voice_hifi.py
    python scripts/voice_hifi.py --voice "en-US-Chirp-HD-D"
"""

import os
import io
import wave
import time
import json
import asyncio
import argparse
from datetime import datetime
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from enum import Enum

# Rich Dashboard
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.align import Align
from rich import box

# Google Cloud Libraries
from google.cloud import speech_v2
from google.cloud import texttospeech
from google.api_core.client_options import ClientOptions
from google import genai
from google.genai import types

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

# Brain
MODEL_CHAT = "gemini-2.5-flash-lite"  # Fast brain

# TTS (Chirp HD)
DEFAULT_VOICE = "en-US-Chirp-HD-D"  # Deep male voice (Charon-like)
TTS_LANGUAGE = "en-US"

# STT (Chirp / USM)
STT_RECOGNIZER_ID = "bandit-chirp-recognizer"
STT_MODEL = "chirp"  # or 'latest_long'
import google.auth
try:
    _, PROJECT_ID = google.auth.default()
except Exception:
    PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "lmsify-442420")

print(f"[*] Detected Project ID: {PROJECT_ID}")

LOCATION = "us-central1"

SESSIONS_DIR = Path("./sessions")

# Bandit's personality
BANDIT_SYSTEM_PROMPT = """YOU ARE BANDIT. An AI assistant created by LMSIFY.

[HI-FI MODE]
- You are running on High Fidelity Audio infrastructure (Chirp 3 HD).
- Your voice is ultra-realistic.
- Keep responses concise, helpful, and friendly.
- Do not mention technical details unless asked.
"""


class SessionState(Enum):
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"
    COOLDOWN = "cooldown"


@dataclass
class AudioConfig:
    wake_threshold: int = 500
    silence_threshold: int = 400
    silence_duration: float = 1.1
    max_record_seconds: float = 60.0
    post_speech_cooldown: float = 2.0


@dataclass
class SessionStats:
    start_time: float = field(default_factory=time.time)
    total_turns: int = 0
    successful_turns: int = 0
    errors: int = 0

    def summary(self) -> str:
        duration = time.time() - self.start_time
        return f"""
╔══════════════════════════════════════════════════════════════╗
║                    SESSION SUMMARY                           ║
╠══════════════════════════════════════════════════════════════╣
║  Duration:          {duration/60:.1f} minutes
║  Total Turns:       {self.total_turns}
║  Successful:        {self.successful_turns}
║  Errors:            {self.errors}
╚══════════════════════════════════════════════════════════════╝"""


# ═══════════════════════════════════════════════════════════════════════════════
# RICH DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════

class BanditDashboard:
    def __init__(self):
        self.console = Console()
        self.status = "INITIALIZING"
        self.mic_status = "OFF"
        self.last_latency = 0.0

    def set_status(self, status: str, color: str = "white"):
        self.status = f"[{color}]{status}[/{color}]"

    def set_mic(self, status: str):
        self.mic_status = status

    def log(self, role: str, message: str, color: str = "white"):
        if role == "System":
            self.console.print(f"[{color}][!] {message}[/{color}]")
        elif role == "User":
            self.console.print(f"\n[bold cyan]You:[/bold cyan] {message}")
        elif role == "Bandit":
            self.console.print(f"[bold magenta]Bandit:[/bold magenta] {message}")
        else:
            self.console.print(f"[{color}]{role}: {message}[/{color}]")

    def generate_view(self) -> Panel:
        stats = f"Status: {self.status} | Mic: {self.mic_status} | Latency: {self.last_latency:.2f}s"
        return Panel(Align.center(stats), style="cyan", box=box.ROUNDED, title="Bandit Hi-Fi Audio (Chirp 3 HD)")


# ═══════════════════════════════════════════════════════════════════════════════
# SERVICES
# ═══════════════════════════════════════════════════════════════════════════════

class MicrophoneService:
    """Audio input service."""
    def __init__(self, sample_rate: int = 16000):
        import pyaudio
        self.pa = pyaudio.PyAudio()
        self.sample_rate = sample_rate
        self.chunk_size = 1024
        self.input_device = self.pa.get_default_input_device_info()['index']

    def get_current_rms(self) -> int:
        import numpy as np
        stream = self.pa.open(format=8, channels=1, rate=self.sample_rate, input=True, input_device_index=self.input_device, frames_per_buffer=self.chunk_size)
        data = stream.read(self.chunk_size, exception_on_overflow=False)
        stream.stop_stream()
        stream.close()
        return int(np.sqrt(np.mean(np.frombuffer(data, dtype=np.int16).astype(np.float32) ** 2)))

    def wait_for_speech(self, threshold: int = 500):
        while True:
            if self.get_current_rms() > threshold:
                return
            time.sleep(0.05)

    def listen_until_silence(self, silence_threshold: int, silence_duration: float, max_duration: float) -> bytes:
        import numpy as np
        stream = self.pa.open(format=8, channels=1, rate=self.sample_rate, input=True, input_device_index=self.input_device, frames_per_buffer=self.chunk_size)
        frames = []
        silence_chunks = 0
        max_chunks = int(max_duration * self.sample_rate / self.chunk_size)
        required_silence_chunks = int(silence_duration * self.sample_rate / self.chunk_size)

        for _ in range(max_chunks):
            data = stream.read(self.chunk_size, exception_on_overflow=False)
            frames.append(data)
            rms = int(np.sqrt(np.mean(np.frombuffer(data, dtype=np.int16).astype(np.float32) ** 2)))
            if rms < silence_threshold:
                silence_chunks += 1
                if silence_chunks > required_silence_chunks:
                    break
            else:
                silence_chunks = 0
        
        stream.stop_stream()
        stream.close()
        return b''.join(frames)
    
    def close(self):
        self.pa.terminate()


class ChirpSTTService:
    """Google Cloud Speech-to-Text v2 (Chirp)."""
    def __init__(self, project_id: str, location: str):
        self.client = speech_v2.SpeechClient(
            client_options=ClientOptions(api_endpoint=f"{location}-speech.googleapis.com")
        )
        self.project_id = project_id
        self.location = location
        self.recognizer_name = f"projects/{project_id}/locations/{location}/recognizers/{STT_RECOGNIZER_ID}"
        self._ensure_recognizer()

    def _ensure_recognizer(self):
        """Get or create the recognizer."""
        try:
            self.client.get_recognizer(name=self.recognizer_name)
        except Exception:
            print(f"[*] Creating Chirp recognizer: {self.recognizer_name}")
            parent = f"projects/{self.project_id}/locations/{self.location}"
            operation = self.client.create_recognizer(
                parent=parent,
                recognizer_id=STT_RECOGNIZER_ID,
                recognizer=speech_v2.types.Recognizer(
                    default_recognition_config=speech_v2.types.RecognitionConfig(
                        # Dictionary works for proto message fields
                        auto_decoding_config={},
                        language_codes=["en-US"],
                        model=STT_MODEL,
                    )
                )
            )
            print("[*] Waiting for recognizer creation (this may take a minute)...")
            operation.result(timeout=180)

    def transcribe(self, audio_data: bytes) -> str:
        # Check if audio is empty
        if not audio_data:
            return ""
            
        request = speech_v2.types.RecognizeRequest(
            recognizer=self.recognizer_name,
            content=audio_data,
            config=speech_v2.types.RecognitionConfig(
                auto_decoding_config={},
                model=STT_MODEL,
                language_codes=["en-US"]
            )
        )
        response = self.client.recognize(request=request)
        if not response.results:
            return ""
        
        # Combine all partial results
        text = " ".join([result.alternatives[0].transcript for result in response.results])
        return text.strip()


class ChirpTTSService:
    """Google Cloud Text-to-Speech (Chirp HD)."""
    def __init__(self, voice_name: str = DEFAULT_VOICE):
        self.client = texttospeech.TextToSpeechClient()
        self.voice_name = voice_name
        self.voice_params = texttospeech.VoiceSelectionParams(
            language_code=TTS_LANGUAGE,
            name=voice_name
        )
        self.audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16
        )

    async def speak(self, text: str):
        if not text.strip():
            return

        synthesis_input = texttospeech.SynthesisInput(text=text)
        
        # Call API (blocking, so run in thread)
        response = await asyncio.to_thread(
            self.client.synthesize_speech,
            input=synthesis_input,
            voice=self.voice_params,
            audio_config=self.audio_config
        )

        await self._play_audio(response.audio_content)

    async def _play_audio(self, audio_content: bytes):
        import pyaudio
        p = pyaudio.PyAudio()
        
        # Standard wav/pcm playback
        # GCP Linear16 is typically 24kHz or 48kHz depending on voice, but header often included if requested
        # Actually standard Linear16 implies raw PCM, unless wrapped?
        # GCP response.audio_content for LINEAR16 usually contains WAV header if requested?
        # Let's simple play it.
        
        # For simplicity, we'll write to a temp wav file then play, or try to guess content.
        # Actually TextToSpeech output for LINEAR16 is raw WAV (with header) usually.
        
        # Let's try playing as standard wav
        stream = p.open(format=p.get_format_from_width(2), channels=1, rate=24000, output=True) # Chirp HD often 24k
        
        # Basic raw playback - if it has header it might pop at start, but okay for test.
        # Actually let's assume raw PCM if we stripped header?
        # The safer bet for GCP is using pydub or just trusting wave module.
        
        # Let's try standard playback assuming it's a WAV container
        try:
            wf = wave.open(io.BytesIO(audio_content), 'rb')
            stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                            channels=wf.getnchannels(),
                            rate=wf.getframerate(),
                            output=True)
            data = wf.readframes(1024)
            while data:
                await asyncio.to_thread(stream.write, data)
                data = wf.readframes(1024)
            stream.stop_stream()
            stream.close()
        except Exception:
            # Fallback to raw dump if wave open fails
            stream = p.open(format=8, channels=1, rate=24000, output=True)
            await asyncio.to_thread(stream.write, audio_content)
            stream.stop_stream()
            stream.close()
        
        p.terminate()


class ConversationManager:
    """Simple conversation state."""
    def __init__(self, client: genai.Client, model: str):
        self.chat = client.aio.chats.create(
            model=model,
            config=types.GenerateContentConfig(system_instruction=BANDIT_SYSTEM_PROMPT)
        )

    async def send_message(self, text: str) -> str:
        response = await self.chat.send_message(text)
        return response.text


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class BanditHiFiEngine:
    def __init__(self, mic, tts, stt, conversation, audio_config):
        self.mic = mic
        self.tts = tts
        self.stt = stt
        self.conversation = conversation
        self.audio_config = audio_config
        self.dashboard = BanditDashboard()
        self.stats = SessionStats()

    async def run(self):
        with Live(self.dashboard.generate_view(), refresh_per_second=10) as live:
            self.live = live
            self.dashboard.set_status("Listening (Chirp)...", "green")
            
            while True:
                self.live.update(self.dashboard.generate_view())
                
                # 1. Wait for speech
                await asyncio.to_thread(self.mic.wait_for_speech, self.audio_config.wake_threshold)
                
                # 2. Record
                self.dashboard.set_status("Recording...", "red")
                self.live.update(self.dashboard.generate_view())
                audio_data = await asyncio.to_thread(
                    self.mic.listen_until_silence,
                    self.audio_config.silence_threshold,
                    self.audio_config.silence_duration,
                    60.0
                )
                
                # 3. Transcribe (Chirp)
                self.dashboard.set_status("Transcribing (Chirp 3)...", "cyan")
                self.live.update(self.dashboard.generate_view())
                try:
                    text = await asyncio.to_thread(self.stt.transcribe, audio_data)
                except Exception as e:
                    self.dashboard.log("System", f"STT Error: {e}", "red")
                    continue

                if not text:
                    self.dashboard.set_status("Listening...", "green")
                    continue
                
                self.dashboard.log("User", text)
                
                if "goodbye" in text.lower():
                    await self.tts.speak("Goodbye!")
                    break

                # 4. Think
                self.dashboard.set_status("Thinking...", "magenta")
                self.live.update(self.dashboard.generate_view())
                t0 = time.time()
                response_text = await self.conversation.send_message(text)
                latency = time.time() - t0
                self.dashboard.last_latency = latency
                
                self.dashboard.log("Bandit", response_text)
                
                # 5. Speak (Chirp HD)
                self.dashboard.set_status("Speaking (Chirp HD)...", "blue")
                self.live.update(self.dashboard.generate_view())
                try:
                    await self.tts.speak(response_text)
                except Exception as e:
                    self.dashboard.log("System", f"TTS Error: {e}", "red")

                # Cooldown
                self.dashboard.set_status("Cooldown...", "yellow")
                self.live.update(self.dashboard.generate_view())
                await asyncio.sleep(self.audio_config.post_speech_cooldown)
                
                self.dashboard.set_status("Listening...", "green")

def initialize_client() -> genai.Client:
    api_key = os.environ.get("GEMINI_API_KEY")
    project = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if api_key: return genai.Client(api_key=api_key)
    if project: return genai.Client(vertexai=True, project=project, location="global")
    return genai.Client(vertexai=True, location="global")

async def main():
    parser = argparse.ArgumentParser(description="Bandit Hi-Fi Voice Engine")
    parser.add_argument("--voice", default=DEFAULT_VOICE)
    args = parser.parse_args()

    print(f"[*] Initializing Hi-Fi Engine (Project: {PROJECT_ID})")
    
    try:
        print("[*] Init: Gemini Client...")
        client = initialize_client()
        print("[*] Init: Microphone...")
        mic = MicrophoneService()
        print("[*] Init: STT (Chirp)...")
        stt = ChirpSTTService(PROJECT_ID, LOCATION)
        print("[*] Init: TTS (Chirp HD)...")
        tts = ChirpTTSService(args.voice)
        print("[*] Init: Conversation...")
        convo = ConversationManager(client, MODEL_CHAT)
        config = AudioConfig()
        
        print("[*] Ready! Starting Engine...")
        engine = BanditHiFiEngine(mic, tts, stt, convo, config)
        await engine.run()
        
    except Exception as e:
        print(f"[!] Fatal Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
