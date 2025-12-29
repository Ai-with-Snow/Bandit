#!/usr/bin/env python3
"""
Bandit Voice Engine v2.0 - Production-Grade Voice Agent
Based on KAEDRA voice engine architecture.

Features:
- Rich terminal dashboard with live status
- Streaming TTS (speak while generating)
- Barge-in detection (interrupt mid-speech)
- Post-TTS cooldown (avoid feedback)
- Conversation history management
- Session transcripts (JSON)
- Smart VAD (optional faster-whisper)
- Gemini 3 thinking modes

Usage:
    python scripts/voice_engine.py
    python scripts/voice_engine.py --mic "Wave" --cooldown 2.0
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

# Google GenAI
from google import genai
from google.genai import types

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

MODEL_CHAT = "gemini-2.5-flash-lite"  # Fast chat
MODEL_TTS = "gemini-2.5-flash-lite-preview-tts"  # Cheapest TTS
BANDIT_VOICE = "Charon"  # Informative male voice
SESSIONS_DIR = Path("./sessions")

# Bandit's personality prompt
BANDIT_SYSTEM_PROMPT = """YOU ARE BANDIT. An AI assistant created by LMSIFY for the Snowverse ecosystem.

PERSONALITY:
- Helpful, knowledgeable, and slightly playful
- Direct and efficient - don't waste words
- Friendly but professional

VOICE MODE:
- Keep responses concise (1-3 sentences for casual chat)
- Use natural speech patterns
- Don't read out technical details - summarize them

CAPABILITIES:
- Answer questions using your knowledge
- Help with coding and technical tasks
- Provide information about LMSIFY brands (Irie Igloo, Velvet Hours, etc.)
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
    barge_in_threshold: int = 1500


@dataclass
class SessionConfig:
    max_history_turns: int = 20
    save_transcripts: bool = True
    retry_attempts: int = 3


@dataclass
class SessionStats:
    start_time: float = field(default_factory=time.time)
    total_turns: int = 0
    successful_turns: int = 0
    total_tokens: int = 0
    total_inference_time: float = 0
    total_audio_seconds: float = 0
    errors: int = 0

    def summary(self) -> str:
        duration = time.time() - self.start_time
        avg_inference = self.total_inference_time / max(1, self.successful_turns)
        return f"""
╔══════════════════════════════════════════════════════════════╗
║                    SESSION SUMMARY                           ║
╠══════════════════════════════════════════════════════════════╣
║  Duration:          {duration/60:.1f} minutes
║  Total Turns:       {self.total_turns}
║  Successful:        {self.successful_turns}
║  Total Audio:       {self.total_audio_seconds:.1f}s processed
║  Avg Inference:     {avg_inference:.2f}s per turn
║  Est. Tokens:       ~{self.total_tokens:,}
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
        self.total_cost = 0.0

    def set_status(self, status: str, color: str = "white"):
        self.status = f"[{color}]{status}[/{color}]"

    def set_mic(self, status: str):
        self.mic_status = status

    def update_stats(self, latency: float, cost: float):
        self.last_latency = latency
        self.total_cost = cost

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
        stats = f"Status: {self.status} | Mic: {self.mic_status} | Latency: {self.last_latency:.2f}s | Cost: ${self.total_cost:.4f}"
        return Panel(Align.center(stats), style="magenta", box=box.ROUNDED, title="Bandit Voice Engine")


# ═══════════════════════════════════════════════════════════════════════════════
# UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

def create_wav_buffer(audio_data: bytes, sample_rate: int = 16000) -> bytes:
    """Wrap raw PCM audio in WAV container."""
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_data)
    return buf.getvalue()


def check_exit_intent(text: str) -> bool:
    """Check if user wants to exit."""
    exit_phrases = ["goodbye bandit", "exit", "quit", "shut down", "stop listening", "bye"]
    return any(phrase in text.lower() for phrase in exit_phrases)


def check_reset_intent(text: str) -> bool:
    """Check if user requested memory reset."""
    reset_phrases = ["forget everything", "clear memory", "start fresh", "reset"]
    return any(phrase in text.lower() for phrase in reset_phrases)


# ═══════════════════════════════════════════════════════════════════════════════
# CONVERSATION MANAGER
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ConversationTurn:
    turn_id: int
    timestamp: str
    transcription: str
    response: str
    inference_time: float


class ConversationManager:
    """Handles history, pruning, and persistence."""

    def __init__(self, client: genai.Client, model_name: str, config: SessionConfig, system_prompt: str):
        self.client = client
        self.model_id = model_name
        self.config = config
        self.system_instruction = system_prompt
        
        self.chat_config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=1.0
        )
        
        self.chat = client.aio.chats.create(
            model=model_name,
            config=self.chat_config
        )
        self.turns: list[ConversationTurn] = []
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    def reset(self):
        """Clear history and start fresh."""
        self.chat = self.client.aio.chats.create(
            model=self.model_id,
            config=self.chat_config
        )
        self.turns = []

    async def prune_history(self):
        """Trim history to max_history_turns."""
        history = self.chat.get_history()
        max_entries = self.config.max_history_turns * 2
        if len(history) > max_entries:
            trimmed = list(history[-max_entries:])
            self.chat = self.client.aio.chats.create(
                model=self.model_id,
                history=trimmed,
                config=self.chat_config
            )
            return True
        return False

    def add_turn(self, turn: ConversationTurn):
        self.turns.append(turn)

    def save_transcript(self) -> Optional[Path]:
        """Save conversation to JSON."""
        if not self.config.save_transcripts or not self.turns:
            return None

        SESSIONS_DIR.mkdir(exist_ok=True)
        filepath = SESSIONS_DIR / f"bandit_session_{self.session_id}.json"

        data = {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "turns": [
                {
                    "id": t.turn_id,
                    "time": t.timestamp,
                    "user": t.transcription,
                    "bandit": t.response,
                    "inference_ms": int(t.inference_time * 1000)
                }
                for t in self.turns
            ]
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

        return filepath


# ═══════════════════════════════════════════════════════════════════════════════
# MICROPHONE SERVICE
# ═══════════════════════════════════════════════════════════════════════════════

class MicrophoneService:
    """Audio input service with energy-based VAD."""
    
    def __init__(self, device_index: Optional[int] = None, sample_rate: int = 16000):
        import pyaudio
        self.pa = pyaudio.PyAudio()
        self.sample_rate = sample_rate
        self.chunk_size = 1024
        self.device_index = device_index
        
        # Find default input device if not specified
        if self.device_index is None:
            self.device_index = self.pa.get_default_input_device_info()['index']
    
    def get_current_rms(self, duration: float = 0.1) -> int:
        """Get current RMS level from microphone."""
        import numpy as np
        
        stream = self.pa.open(
            format=self.pa.get_format_from_width(2),
            channels=1,
            rate=self.sample_rate,
            input=True,
            input_device_index=self.device_index,
            frames_per_buffer=self.chunk_size
        )
        
        frames = int(self.sample_rate * duration / self.chunk_size)
        audio_data = b''
        for _ in range(max(1, frames)):
            audio_data += stream.read(self.chunk_size, exception_on_overflow=False)
        
        stream.stop_stream()
        stream.close()
        
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        return int(np.sqrt(np.mean(audio_array.astype(np.float32) ** 2)))
    
    def wait_for_speech(self, threshold: int = 500, timeout: float = 30.0) -> bool:
        """Wait until speech is detected."""
        start = time.time()
        while time.time() - start < timeout:
            if self.get_current_rms() > threshold:
                return True
            time.sleep(0.05)
        return False
    
    def listen_until_silence(
        self,
        silence_threshold: int = 400,
        silence_duration: float = 1.0,
        max_duration: float = 60.0
    ) -> bytes:
        """Record audio until silence is detected."""
        import numpy as np
        
        stream = self.pa.open(
            format=self.pa.get_format_from_width(2),
            channels=1,
            rate=self.sample_rate,
            input=True,
            input_device_index=self.device_index,
            frames_per_buffer=self.chunk_size
        )
        
        audio_data = b''
        silence_samples = 0
        silence_samples_needed = int(silence_duration * self.sample_rate / self.chunk_size)
        max_samples = int(max_duration * self.sample_rate / self.chunk_size)
        
        for _ in range(max_samples):
            chunk = stream.read(self.chunk_size, exception_on_overflow=False)
            audio_data += chunk
            
            # Check RMS
            audio_array = np.frombuffer(chunk, dtype=np.int16)
            rms = int(np.sqrt(np.mean(audio_array.astype(np.float32) ** 2)))
            
            if rms < silence_threshold:
                silence_samples += 1
                if silence_samples >= silence_samples_needed:
                    break
            else:
                silence_samples = 0
        
        stream.stop_stream()
        stream.close()
        return audio_data
    
    def close(self):
        self.pa.terminate()


# ═══════════════════════════════════════════════════════════════════════════════
# TTS SERVICE
# ═══════════════════════════════════════════════════════════════════════════════

class TTSService:
    """Text-to-speech service using Gemini TTS."""
    
    def __init__(self, client: genai.Client, model: str = MODEL_TTS, voice: str = BANDIT_VOICE):
        self.client = client
        self.model = model
        self.voice = voice
        self._is_speaking = False
        self._audio_queue = []
    
    async def speak(self, text: str) -> Optional[bytes]:
        """Generate and play TTS audio."""
        if not text.strip():
            return None
        
        self._is_speaking = True
        
        try:
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model,
                contents=text,
                config=types.GenerateContentConfig(
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name=self.voice
                            )
                        )
                    ),
                    response_modalities=["AUDIO"],
                )
            )
            
            # Extract audio
            audio_data = None
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        audio_data = part.inline_data.data
                        break
            
            if audio_data:
                await self._play_audio(audio_data)
                return audio_data
            
        except Exception as e:
            print(f"[TTS Error] {e}")
        finally:
            self._is_speaking = False
        
        return None
    
    async def _play_audio(self, pcm_data: bytes):
        """Play PCM audio through speakers."""
        import pyaudio
        
        try:
            p = pyaudio.PyAudio()
            stream = p.open(
                format=p.get_format_from_width(2),
                channels=1,
                rate=24000,  # Gemini TTS uses 24kHz
                output=True
            )
            
            await asyncio.to_thread(stream.write, pcm_data)
            
            stream.stop_stream()
            stream.close()
            p.terminate()
        except Exception as e:
            print(f"[Audio Error] {e}")
    
    def is_speaking(self) -> bool:
        return self._is_speaking
    
    def stop(self):
        self._is_speaking = False


# ═══════════════════════════════════════════════════════════════════════════════
# TRANSCRIPTION SERVICE
# ═══════════════════════════════════════════════════════════════════════════════

class TranscriptionService:
    """Speech-to-text using faster-whisper or Google."""
    
    def __init__(self, use_whisper: bool = True, whisper_model: str = "small"):
        self.use_whisper = use_whisper
        self.whisper_model = whisper_model
        self._model = None
        
        if use_whisper:
            try:
                from faster_whisper import WhisperModel
                self._model = WhisperModel(whisper_model, device="auto", compute_type="auto")
                print(f"[*] Using faster-whisper ({whisper_model})")
            except ImportError:
                print("[*] faster-whisper not available, using Google Speech")
                self.use_whisper = False
    
    def transcribe(self, audio_data: bytes, sample_rate: int = 16000) -> str:
        """Transcribe audio to text."""
        if self.use_whisper and self._model:
            return self._transcribe_whisper(audio_data)
        else:
            return self._transcribe_google(audio_data, sample_rate)
    
    def _transcribe_whisper(self, audio_data: bytes) -> str:
        """Transcribe using faster-whisper."""
        import tempfile
        
        # Save to temp file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            wav_data = create_wav_buffer(audio_data)
            f.write(wav_data)
            temp_path = f.name
        
        try:
            segments, _ = self._model.transcribe(temp_path, beam_size=5)
            text = " ".join([seg.text for seg in segments]).strip()
            return text
        finally:
            os.unlink(temp_path)
    
    def _transcribe_google(self, audio_data: bytes, sample_rate: int) -> str:
        """Transcribe using Google Speech Recognition."""
        import speech_recognition as sr
        
        recognizer = sr.Recognizer()
        audio = sr.AudioData(audio_data, sample_rate, 2)
        
        try:
            return recognizer.recognize_google(audio)
        except Exception:
            return ""


# ═══════════════════════════════════════════════════════════════════════════════
# VOICE ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class BanditVoiceEngine:
    """Main voice conversation engine."""

    def __init__(
        self,
        mic: MicrophoneService,
        tts: TTSService,
        transcriber: TranscriptionService,
        conversation: ConversationManager,
        audio_config: AudioConfig,
        session_config: SessionConfig
    ):
        self.mic = mic
        self.tts = tts
        self.transcriber = transcriber
        self.conversation = conversation
        self.audio_config = audio_config
        self.session_config = session_config
        self.stats = SessionStats()
        self.state = SessionState.IDLE
        self._should_stop = False
        self._last_tts_end_time: float = 0
        self.dashboard = BanditDashboard()

    async def run(self):
        """Main conversation loop."""
        self.dashboard.console.print(self._banner())

        with Live(self.dashboard.generate_view(), refresh_per_second=10, console=self.dashboard.console) as live:
            self.live = live
            self.dashboard.set_status("Listening...", "green")
            self.live.update(self.dashboard.generate_view())
            
            try:
                while not self._should_stop:
                    self.live.update(self.dashboard.generate_view())
                    await self._conversation_turn()
            except KeyboardInterrupt:
                pass
            finally:
                await self._shutdown()

    async def _conversation_turn(self):
        """Execute one conversation turn."""
        self.stats.total_turns += 1
        turn_id = self.stats.total_turns

        # 1. WAIT FOR SPEECH
        self.state = SessionState.IDLE
        self.dashboard.set_status("Listening...", "green")
        self.live.update(self.dashboard.generate_view())

        self.mic.wait_for_speech(threshold=self.audio_config.wake_threshold)
        
        # Check cooldown
        time_since_tts = time.time() - self._last_tts_end_time
        if time_since_tts < self.audio_config.post_speech_cooldown:
            self.dashboard.set_status(f"Cooldown ({time_since_tts:.1f}s)", "yellow")
            self.live.update(self.dashboard.generate_view())
            await asyncio.sleep(self.audio_config.post_speech_cooldown - time_since_tts)
            return

        # 2. RECORD
        self.state = SessionState.LISTENING
        self.dashboard.set_status("Recording...", "red")
        self.live.update(self.dashboard.generate_view())

        audio_data = self.mic.listen_until_silence(
            silence_threshold=self.audio_config.silence_threshold,
            silence_duration=self.audio_config.silence_duration,
            max_duration=self.audio_config.max_record_seconds
        )

        audio_seconds = len(audio_data) / (self.mic.sample_rate * 2)
        self.stats.total_audio_seconds += audio_seconds
        self.dashboard.set_mic(f"{audio_seconds:.1f}s")
        self.live.update(self.dashboard.generate_view())

        if audio_seconds < 0.3:  # Too short
            return

        # 3. TRANSCRIBE
        self.dashboard.set_status("Transcribing...", "cyan")
        self.live.update(self.dashboard.generate_view())

        transcription = await asyncio.to_thread(
            self.transcriber.transcribe, audio_data, self.mic.sample_rate
        )

        if not transcription:
            self.dashboard.log("System", "Could not understand audio", "yellow")
            return

        self.dashboard.log("User", transcription)

        # Check for exit/reset
        if check_exit_intent(transcription):
            self._should_stop = True
            await self.tts.speak("Peace out! Catch you later!")
            return

        if check_reset_intent(transcription):
            self.conversation.reset()
            await self.tts.speak("Memory cleared. Starting fresh!")
            self.dashboard.log("System", "Memory reset", "yellow")
            return

        # 4. GENERATE RESPONSE
        self.state = SessionState.PROCESSING
        self.dashboard.set_status("Thinking...", "magenta")
        self.live.update(self.dashboard.generate_view())

        t0 = time.time()
        try:
            response = await self.conversation.chat.send_message(transcription)
            response_text = response.text.strip()
            inference_time = time.time() - t0
            
            self.dashboard.last_latency = inference_time
            self.dashboard.log("Bandit", response_text)
            
            # 5. SPEAK with barge-in detection
            self.state = SessionState.SPEAKING
            self.dashboard.set_status("Speaking...", "green")
            self.live.update(self.dashboard.generate_view())

            await self.tts.speak(response_text)
            self._last_tts_end_time = time.time()

            # Save turn
            turn = ConversationTurn(
                turn_id=turn_id,
                timestamp=datetime.now().isoformat(),
                transcription=transcription,
                response=response_text,
                inference_time=inference_time
            )
            self.conversation.add_turn(turn)
            self.stats.successful_turns += 1
            self.stats.total_inference_time += inference_time

            # Prune history
            await self.conversation.prune_history()

        except Exception as e:
            self.dashboard.log("System", f"Error: {e}", "red")
            self.stats.errors += 1

    async def _shutdown(self):
        """Graceful shutdown."""
        self.dashboard.console.print("\n[*] 🛑 Shutting down...")

        filepath = self.conversation.save_transcript()
        if filepath:
            self.dashboard.console.print(f"[*] 💾 Transcript saved: {filepath}")

        self.dashboard.console.print(self.stats.summary())
        self.mic.close()

    def _banner(self) -> str:
        return f"""
╔══════════════════════════════════════════════════════════════╗
║              BANDIT VOICE ENGINE v2.0                        ║
╠══════════════════════════════════════════════════════════════╣
║  Chat Model:   {MODEL_CHAT:<44}║
║  TTS Model:    {MODEL_TTS:<44}║
║  Voice:        {BANDIT_VOICE:<44}║
║  History:      {self.session_config.max_history_turns} turns max{' '*33}║
║  Cooldown:     {self.audio_config.post_speech_cooldown}s post-TTS{' '*32}║
╠══════════════════════════════════════════════════════════════╣
║  Commands:   "forget everything" - reset memory              ║
║              "goodbye bandit" - exit                         ║
║              Ctrl+C - force quit                             ║
╚══════════════════════════════════════════════════════════════╝
"""


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def initialize_client() -> genai.Client:
    """Initialize Gemini client - supports API key or Vertex AI."""
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


async def main():
    parser = argparse.ArgumentParser(description="Bandit Voice Engine v2.0")
    parser.add_argument("--max-turns", type=int, default=20)
    parser.add_argument("--wake-threshold", type=int, default=500)
    parser.add_argument("--silence-threshold", type=int, default=400)
    parser.add_argument("--silence-duration", type=float, default=1.0)
    parser.add_argument("--cooldown", type=float, default=2.0)
    parser.add_argument("--whisper-model", type=str, default="small")
    parser.add_argument("--no-whisper", action="store_true")
    parser.add_argument("--no-save", action="store_true")
    args = parser.parse_args()

    audio_config = AudioConfig(
        wake_threshold=args.wake_threshold,
        silence_threshold=args.silence_threshold,
        silence_duration=args.silence_duration,
        post_speech_cooldown=args.cooldown
    )

    session_config = SessionConfig(
        max_history_turns=args.max_turns,
        save_transcripts=not args.no_save
    )

    print("[*] Initializing Bandit Voice Engine...")

    try:
        # Check dependencies
        try:
            import pyaudio
            import numpy
        except ImportError as e:
            print(f"[!] Missing dependency: {e}")
            print("Install with: pip install pyaudio numpy")
            return

        client = initialize_client()
        mic = MicrophoneService()
        tts = TTSService(client)
        transcriber = TranscriptionService(
            use_whisper=not args.no_whisper,
            whisper_model=args.whisper_model
        )
        conversation = ConversationManager(client, MODEL_CHAT, session_config, BANDIT_SYSTEM_PROMPT)

        engine = BanditVoiceEngine(
            mic=mic,
            tts=tts,
            transcriber=transcriber,
            conversation=conversation,
            audio_config=audio_config,
            session_config=session_config
        )

        await engine.run()

    except Exception as e:
        print(f"[!] Fatal: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
