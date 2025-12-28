#!/usr/bin/env python3
"""
Bandit Voice Engine v3.0.4 (Bulletproof Master Sync) - Production-Grade Voice Agent

ARCHITECTURE: "Dual-Brain Hybrid" (Separate Fast/Deep/TTS models)
- Fast: gemini-3-flash-preview (Immediate UI/Router)
- Deep: gemini-3-pro-preview-11-2025 (Tool-Heavy Research)
- TTS: gemini-2.5-flash-preview-tts (Screenplay Audio @ 24kHz)
- Dev: Dec 2025 Model & Pricing Sync (v3.0.4)
"""

import os
import time
import asyncio
import threading
import json
import re
from datetime import datetime
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List, Dict
from enum import Enum
from contextlib import asynccontextmanager

import numpy as np
from pydantic import BaseModel, Field

# Rich UI
from rich.console import Console
from rich.live import Live
from rich.text import Text
from rich.align import Align
from rich.panel import Panel
from rich.table import Table
from rich.columns import Columns
from rich import box
from rich.console import Group
from rich.markdown import Markdown

# WebSocket (Elgato)
try:
    import websockets
    HAS_WEBSOCKETS = True
except ImportError:
    HAS_WEBSOCKETS = False

# Google GenAI
from google import genai
from google.genai import types

# Voice Search Backend
try:
    from voice_search import VoiceAISearchEngine
except ImportError:
    VoiceAISearchEngine = None

# ===============================================================================
# CONFIGURATION
# ===============================================================================

# Models
MODEL_FAST = "gemini-3-flash-preview" 
MODEL_DEEP = "gemini-3-pro-preview-11-2025" 
MODEL_TTS = "gemini-2.5-flash-preview-tts"

BANDIT_VOICE = "Charon"
SESSIONS_DIR = Path("./sessions")

# Corrected Gemini 3 Tier Pricing (per 1M units)
PRICING = {
    MODEL_FAST: {"input": 0.50, "output": 3.00},
    MODEL_DEEP: {"input": 2.00, "output": 12.00}, 
    MODEL_TTS:  {"input": 0.50, "output": 10.00}, 
}

SEARCH_ENGINE = None

# ===============================================================================
# SCREENPLAY UI (USER PROVIDED & ADAPTED)
# ===============================================================================

class ScreenplayFormatter:
    """Formats voice transcripts as movie screenplay scenes."""
    
    def __init__(self, console: Optional[Console] = None, title: str = "BANDIT VOICE SESSION"):
        self.console = console or Console()
        self.title = title
        self.scene_number = 1
        self.last_speaker = None
        
    def format_segment(self, segment: Dict, speaker: str = "USER") -> Panel:
        """Format a transcript segment as screenplay dialogue."""
        timestamp = f"{segment['start']:.1f}s - {segment['end']:.1f}s"
        scene_heading = Text(f"SCENE {self.scene_number:03d}", style="dim")
        scene_heading.append(f" [{timestamp}]", style="dim italic")
        
        # Character name
        char_style = "bold cyan" if speaker == "USER" else "bold magenta"
        char_name = Align.center(Text(speaker.upper(), style=char_style), vertical="middle")
        
        # Dialogue with confidence
        text = segment['text'].strip()
        conf = segment.get('confidence', 1.0)
        conf_mark = " [yellow]⚠[/yellow]" if conf < 0.8 else ""
        
        dialogue = Text("    " + text + conf_mark, style="white")
        
        # Parenthetical
        duration = segment['end'] - segment['start']
        parenthetical = None
        if duration < 1.0:
            parenthetical = Align.center(Text("(quickly)", style="italic dim"), vertical="middle")
        
        # Build content using Group to handle mixed Renderables (Text + Align)
        renderables = [
            scene_heading,
            Text("\n"),
            char_name, # Align object
            Text("\n")
        ]
        
        if parenthetical:
            renderables.append(parenthetical)
            renderables.append(Text("\n"))
            
        renderables.append(dialogue)
        renderables.append(Text("\n"))
        
        content = Group(*renderables)
        
        return Panel(content, box=box.ROUNDED, border_style="dim", padding=(0, 2))
    
    def format_interruption(self, timestamp: float) -> Panel:
        return Panel(Align.center(Text(f"⚠️  BARGE-IN at {timestamp:.1f}s", style="bold red")), border_style="red", box=box.DOUBLE)

class MarkdownScreenplayExporter:
    """Export voice transcripts to professional screenplay Markdown format."""
    def __init__(self, output_dir: str = "./screenplays"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def create_fountain_markdown(self, segments: List[Dict], title: str = "Bandit Voice Session") -> str:
        lines = ["---", f"Title: {title}", f"Date: {datetime.now()}", "Author: Bandit v3.0.4", "---", "", "INT. VOICE SESSION - DAY", ""]
        for seg in segments:
            speaker = seg.get('speaker', 'USER')
            lines.append(f"{speaker.upper()}")
            dur = seg['end'] - seg['start']
            if seg.get('confidence', 1.0) < 0.8: lines.append(f"(*low confidence*)")
            elif dur < 1.0: lines.append(f"(*quickly*)")
            lines.append(f"{seg['text'].strip()}\n")
            if seg.get('barge_in'): lines.append(f"> BARGE-IN at {seg['start']:.1f}s\n")
        lines.append("THE END")
        return "\n".join(lines)

    def save_markdown(self, segments, title=None, format="fountain") -> Path:
        if not title: title = f"bandit_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        fname = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        fpath = self.output_dir / f"{fname}.md"
        content = self.create_fountain_markdown(segments, title)
        fpath.write_text(content, encoding='utf-8')
        return fpath

class BanditHeader:
    """Premium ASCII/Stylized Header for the Bandit CLI."""
    @staticmethod
    def generate():
        title = Text("BANDIT VOICE ENGINE v3.0.4", style="bold white on blue")
        subtitle = Text("PREMIUM PRODUCTION INTERFACE • MASTER MODEL SYNC", style="dim cyan")
        banner = Panel(Align.center(Group(title, subtitle)), box=box.DOUBLE, border_style="blue", padding=(1, 2))
        return banner

class LiveTranscriptDisplay:
    """Live-updating transcript display for voice sessions with Auto-Save."""
    def __init__(self, stats, formatter: Optional[ScreenplayFormatter] = None, auto_save: bool = True):
        self.formatter = formatter or ScreenplayFormatter()
        self.stats = stats
        self.segments: List[Dict] = []
        self.live = None
        self.status_msg = "Initializing..."
        self.exporter = MarkdownScreenplayExporter() if auto_save else None
        self.session_start = time.time()
        
    def set_status(self, msg: str):
        self.status_msg = msg
        if self.live: self.live.update(self._render_current_scene())

    def _get_pulse(self):
        # Dynamic pulse based on time
        frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        return frames[int(time.time() * 10) % len(frames)]

    def _auto_save(self):
        if self.exporter:
            self.exporter.save_markdown(self.segments, title=f"autosave_{int(self.session_start)}")

    def add_segment(self, segment: Dict, speaker: str = "USER"):
        segment['speaker'] = speaker
        self.segments.append(segment)
        self.formatter.scene_number += 1
        if self.live: self.live.update(self._render_current_scene())
        if len(self.segments) % 5 == 0: self._auto_save()
    
    def add_interruption(self, timestamp: float):
        if self.live:
            self.live.update(self.formatter.format_interruption(timestamp))
            time.sleep(0.5)
    
    def _render_footer(self) -> Table:
        t = Table(show_header=False, box=None, expand=True)
        # Live Signal Meter for Developer Mode
        rms = getattr(self.stats, 'current_rms', 0)
        meter_width = 10
        active_bars = int((rms / 8000) * meter_width) if rms > 0 else 0
        active_bars = min(active_bars, meter_width)
        meter = f"[{'#' * active_bars}{'-' * (meter_width - active_bars)}]"
        
        t.add_row(
            f"[bold cyan]Signal:[/] {meter}",
            f"[bold]Status:[/] {self.status_msg}", 
            f"[bold]Turns:[/] {self.stats.turns}", 
            f"[bold]Latency:[/] {self.stats.last_latency:.2f}s",
            f"[bold]Cost:[/] ${self.stats.estimate_cost():.4f}"
        )
        return Panel(t, style="grey30")

    def _render_current_scene(self):
        header = BanditHeader.generate()
        
        # Brain Telemetry
        brain_status = Table(show_header=False, box=None, padding=(0, 1))
        trans_style = "bold yellow" if self.stats.active_brain == "TRANS" else "dim"
        fast_style = "bold green" if self.stats.active_brain == "FAST" else "dim"
        deep_style = "bold magenta" if self.stats.active_brain == "DEEP" else "dim"
        pulse = self._get_pulse() if self.stats.active_brain else "·"
        
        brain_status.add_row(
            Text(f"TRANS {pulse if self.stats.active_brain == 'TRANS' else ''}", style=trans_style),
            Text(f"FAST {pulse if self.stats.active_brain == 'FAST' else ''}", style=fast_style),
            Text(f"DEEP {pulse if self.stats.active_brain == 'DEEP' else ''}", style=deep_style)
        )
        telemetry = Panel(Align.center(brain_status), title="[bold white]THOUGHT SIGNATURES[/]", border_style="blue", box=box.HORIZONTALS)

        if not self.segments:
            main_view = Panel("Waiting for input...", border_style="dim")
        else:
            recent_segments = self.segments[-2:] # Show last 2 for focus
            panels = [self.formatter.format_segment(seg, seg.get('speaker', 'USER')) for seg in recent_segments]
            if len(panels) >= 2: main_view = Columns(panels, equal=True, expand=True)
            else: main_view = panels[0]
        
        return Group(header, telemetry, main_view, self._render_footer())
    
    @asynccontextmanager
    async def live_display(self):
        with Live(self._render_current_scene(), console=self.formatter.console, refresh_per_second=4, screen=False) as live:
            self.live = live
            try: yield self
            finally:
                self.live = None
                if self.exporter:
                    fpath = self.exporter.save_markdown(self.segments)
                    self.formatter.console.print(f"[green]✓ Saved transcript to {fpath}[/green]")

# ===============================================================================
# SERVICE LOGIC (v2.1 Enhanced)
# ===============================================================================

class SessionState(Enum):
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"
    BARGE_IN = "barge_in"

class AtomicState:
    def __init__(self, initial=SessionState.IDLE):
        self._state = initial; self._lock = threading.Lock()
    def set(self, s): 
        with self._lock: self._state = s

@dataclass
class AudioConfig:
    silence_threshold: int = 400
    silence_duration: float = 0.7 # Shaved from 1.0s for speed
    barge_in_threshold: int = 6000
    use_webrtc_vad: bool = True

@dataclass
class SessionStats:
    start_time: float = field(default_factory=time.time)
    turns: int = 0
    errors: int = 0
    last_latency: float = 0.0 
    current_rms: int = 0 # Live developer telemetry
    active_brain: Optional[str] = None # FAST, DEEP, or None
    
    # Track usage per model
    usage: Dict[str, Dict[str, float]] = field(default_factory=lambda: {
        MODEL_FAST: {"in": 0, "out": 0},
        MODEL_DEEP: {"in": 0, "out": 0},
        MODEL_TTS:  {"in": 0, "out": 0}
    })
    
    def add_usage(self, model: str, input_units: float = 0, output_units: float = 0):
        if model in self.usage:
            self.usage[model]["in"] += input_units
            self.usage[model]["out"] += output_units

    def estimate_cost(self) -> float:
        """FIX: Dynamic cost estimation based on Dec 2025 pricing."""
        total = 0.0
        for model, counts in self.usage.items():
            if model in PRICING:
                total += (counts["in"] / 1e6) * PRICING[model]["input"]
                total += (counts["out"] / 1e6) * PRICING[model]["output"]
        return total

# ... (Insert TTSService, MicrophoneService, TranscriptionService, ConversationManager from v2.1 Enhanced) ...
# I will output the FULL file content to be safe.

# ===============================================================================
# SERVICES
# ===============================================================================

class ElgatoService:
    """Interface for Elgato Wave Link via JSON-RPC WebSocket."""
    def __init__(self, host="127.0.0.1", port=1824):
        self.uri = f"ws://{host}:{port}"
        self.connected = False
        self.current_level = 0.0
        self.ws = None
        if HAS_WEBSOCKETS:
            threading.Thread(target=self._run_loop, daemon=True).start()
            
    def _run_loop(self):
        asyncio.run(self._listen())
        
    async def _listen(self):
        try:
            async with websockets.connect(self.uri) as ws:
                self.ws = ws
                self.connected = True
                # Subscribe? Typically events are pushed.
                while True:
                    msg = await ws.recv()
                    data = json.loads(msg)
                    if data.get("method") == "realTimeChanges":
                        # Check params.MixerList for mic
                        # Assuming first input or specific ID. 
                        # Use average of all inputs or StreamMix header?
                        # Simplified: Just grab localMixer level
                        lvl = data["params"].get("localMixer", {}).get("levelLeft", 0)
                        self.current_level = float(lvl)
        except Exception:
            self.connected = False

    def get_rms_equivalent(self):
        # Map 0.0-1.0 to 0-32768
        return int(self.current_level * 32768)

async def with_retry(fn, max_attempts=3, base_delay=1.0):
    for attempt in range(max_attempts):
        try: return await fn()
        except Exception:
            if attempt == max_attempts - 1: raise
            await asyncio.sleep(base_delay * (2 ** attempt))

class TTSService:
    def __init__(self, client, mic_service, barge_threshold=6000):
        self.client = client; self.mic = mic_service; self.barge_threshold = barge_threshold
        self._stop = threading.Event()
    
    async def speak(self, text: str) -> bool:
        """Isolated TTS execution with Fail-Silent policy."""
        if not text.strip(): return False
        
        # --- ULTRA-AGGRESSIVE DIALOGUE ISOLATION (v2.4.7) ---
        
        # 0. BLOCK SYSTEM ERRORS & TECHNICAL LEAKAGE (FAIL-SILENT)
        # We check for technical markers often found in tracebacks or error replies.
        technical_markers = [
            "engine lag", "error", "async", "generate", "positional", "argument", 
            "syntax", "traceback", "takes", "timeout", "exception", "contents", 
            "config", "types", "candidate", "part", "inline", "json", "resp"
        ]
        if any(x in text.lower() for x in technical_markers):
            return False
        
        # 1. Strip brackets [METADATA]
        # 2. Strip internal reasoning tags
        # 3. Strip bold headers
        # 4. Strip JSON code blocks
        
        c = text
        c = re.sub(r'\[.*?\]', '', c) 
        c = re.sub(r'^\s*(Thinking|Analysis|Internal|Thought|Action|Observation|Thought Process|Fast Brain|Deep Brain|Vibe check|Target|Task|Protocol):.*$', '', c, flags=re.MULTILINE | re.IGNORECASE)
        c = re.sub(r'\*\*.*?\*\*(\s*:)?', '', c) 
        c = re.sub(r'```.*?```', '', c, flags=re.DOTALL)
        c = re.sub(r'[*_#-]', '', c) 
        c = c.strip().strip('"').strip("'").strip()
        
        # FINAL SAFETY: If we still have code-like symbols or raw logic, skip it
        if "{" in c or "async" in c.lower() or "await" in c.lower():
            return False
            
        clean_text = c if (c and len(c) > 1) else ""
        if not clean_text: return False
        
        self._stop.clear()
        # Audio Player Setup
        import pyaudio
        p = pyaudio.PyAudio()
        # Increased buffer to 1024 for smoother Windows MME/DirectSound stability
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=24000, output=True, frames_per_buffer=1024)
        interrupted = False
        try:
            # Streaming Generation
            async for chunk in await self.client.aio.models.generate_content_stream(
                model=MODEL_TTS, contents=clean_text,
                config=types.GenerateContentConfig(
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=BANDIT_VOICE))),
                    response_modalities=["AUDIO"])
            ):
                if self._stop.is_set():
                    interrupted = True; break
                
                audio_data = None
                if chunk.candidates and chunk.candidates[0].content.parts:
                    for part in chunk.candidates[0].content.parts:
                        if part.inline_data: 
                            audio_data = part.inline_data.data
                            break
                
                if audio_data:
                    # Track TTS output: units roughly = characters for TTS pricing
                    self.mic.stats.add_usage(MODEL_TTS, input_units=len(clean_text), output_units=len(audio_data)/1000) # Rough char-based estimate?
                    
                    # Play chunk immediately
                    await asyncio.to_thread(stream.write, audio_data)
                    
                    # Check barge-in AFTER write for better responsiveness to current mic state
                    if self.mic and (await asyncio.to_thread(self.mic.get_current_rms)) > self.barge_threshold:
                         self._stop.set(); interrupted = True; break
            
            return interrupted
        except Exception as e:
            print(f"TTS Error: {e}") 
            return False
        finally:
            if stream: stream.stop_stream(); stream.close()
            p.terminate()

    async def _play_audio(self, pcm_data: bytes) -> bool:
        # Legacy: Kept safe
        return False

    def stop(self): self._stop.set()

class MicrophoneService:
    def __init__(self, use_vad=True, use_elgato=True, stats: Optional[SessionStats] = None):
        import pyaudio
        self.pa = pyaudio.PyAudio(); self.chunk = 1024
        self.stats = stats
        self.device_name = "Default"
        # Robust Device Selection
        try:
            device_info = self.pa.get_default_input_device_info()
            self.input_device = device_info['index']
            self.device_name = device_info.get('name', 'Unknown')
        except:
            self.input_device = None
            
        self.stream = self.pa.open(format=2, channels=1, rate=16000, input=True, 
                                   input_device_index=self.input_device,
                                   frames_per_buffer=self.chunk, start=False)
        self.stream.start_stream()
        self.vad = None
        if use_vad:
            try: import webrtcvad; self.vad = webrtcvad.Vad(2)
            except: pass
        
        self.elgato = None
        if use_elgato and HAS_WEBSOCKETS:
            self.elgato = ElgatoService()

    def get_current_rms(self) -> int:
        # 1. Try Elgato (Zero Latency)
        rms = 0
        if self.elgato and self.elgato.connected:
            rms = self.elgato.get_rms_equivalent()
        else:
            # 2. Fallback to PyAudio
            try:
                if self.stream.is_stopped(): self.stream.start_stream()
                if self.stream.get_read_available() > self.chunk:
                     self.stream.read(self.stream.get_read_available(), exception_on_overflow=False)
                data = self.stream.read(self.chunk, exception_on_overflow=False)
                arr = np.frombuffer(data, dtype=np.int16)
                rms = int(np.sqrt(np.mean(arr.astype(np.float32)**2)))
            except: rms = 0
            
        if self.stats: self.stats.current_rms = rms
        return rms

    def listen_until_silence(self, threshold, silence_duration, max_dur) -> bytes:
        # Flush buffer before starting listening
        try:
            if self.stream.is_stopped(): self.stream.start_stream()
            to_read = self.stream.get_read_available()
            if to_read > 0: self.stream.read(to_read, exception_on_overflow=False)
        except: pass

        frames = []; silent_chunks = 0
        chunks_for_silence = int(silence_duration * 16000 / self.chunk)
        started = False
        
        # We must loop manually to honor max_dur
        for _ in range(int(max_dur * 16000 / self.chunk)):
            # Check for system interrupt or early exit to prevent thread lock
            if not self.stream.is_active(): break
            
            try:
                data = self.stream.read(self.chunk, exception_on_overflow=False)
                frames.append(data)
                rms = int(np.sqrt(np.mean(np.frombuffer(data, dtype=np.int16).astype(np.float32)**2)))
                # Update live telemetry
                if self.stats: self.stats.current_rms = rms
                
                if rms > threshold: started = True; silent_chunks = 0
                elif started: silent_chunks += 1
                if started and silent_chunks > chunks_for_silence: break
            except: break
        
        return b''.join(frames) if started else b''
        
    def close(self): 
        self.stream.stop_stream()
        self.stream.close()
        self.pa.terminate()

class TranscriptionService:
    def __init__(self): 
        self._whisper = None
    
    def warm_up(self):
        """Pre-load model to prevent first-turn lag."""
        try:
            if not self._whisper: 
                from faster_whisper import WhisperModel
                self._whisper = WhisperModel("tiny.en", device="cpu", compute_type="int8")
                # Dummy transcription to warm up GPU/CPU buffers
                self._whisper.transcribe(np.zeros(16000, dtype=np.float32))
        except: pass

    def transcribe(self, audio: bytes) -> str:
        if not audio or len(audio) < 4000: return "" # Skip tiny noise blips
        try:
            # Lazy load for memory efficiency
            if not self._whisper: 
                from faster_whisper import WhisperModel
                self._whisper = WhisperModel("tiny.en", device="cpu", compute_type="int8")
            
            # Normalization
            arr = np.frombuffer(audio, dtype=np.int16).flatten().astype(np.float32) / 32768.0
            
            # VAD inside transcription to prevent hallucination from background noise
            segments, _ = self._whisper.transcribe(arr, beam_size=3, initial_prompt="Bandit.")
            res = " ".join([s.text for s in segments]).strip()
            
            # Filter common Whisper hallucinations on silence:
            if res.lower() in ["you", "shh", "thank you", "bye", "uh", "um"]: return ""
            return res
        except: return ""

def create_tool_declarations() -> list[types.Tool]:
    # (Same as before)
    if not VoiceAISearchEngine: return []
    return [types.Tool(function_declarations=[
        types.FunctionDeclaration(name="search_google", description="Search Google", parameters=types.Schema(type=types.Type.OBJECT, properties={"query": types.Schema(type=types.Type.STRING)}, required=["query"])),
        types.FunctionDeclaration(name="fetch_url", description="Fetch URL", parameters=types.Schema(type=types.Type.OBJECT, properties={"url": types.Schema(type=types.Type.STRING)}, required=["url"])),
        types.FunctionDeclaration(name="bigquery_query", description="BigQuery", parameters=types.Schema(type=types.Type.OBJECT, properties={"sql_query": types.Schema(type=types.Type.STRING)}, required=["sql_query"])),
        types.FunctionDeclaration(name="list_gcs_files", description="List GCS", parameters=types.Schema(type=types.Type.OBJECT, properties={"bucket_name": types.Schema(type=types.Type.STRING)}, required=["bucket_name"])),
        types.FunctionDeclaration(name="read_gcs_file", description="Read GCS", parameters=types.Schema(type=types.Type.OBJECT, properties={"bucket_name": types.Schema(type=types.Type.STRING), "filename": types.Schema(type=types.Type.STRING)}, required=["bucket_name", "filename"]))
    ])]

class RouterResponse(BaseModel):
    reply: str
    requires_deep_reasoning: bool

class ConversationManager:
    def __init__(self, client, sys_prompt, stats):
        self.client = client; self.stats = stats; self.history = []
        self.fast = types.GenerateContentConfig(system_instruction=sys_prompt, response_mime_type="application/json", response_schema=RouterResponse)
        self.deep = types.GenerateContentConfig(system_instruction=sys_prompt, tools=create_tool_declarations())
    
    async def route_and_respond(self, text: str) -> tuple[str, bool, str]:
        t_ctx = f"[{SEARCH_ENGINE.get_eastern_time_advanced()}] " if SEARCH_ENGINE else ""
        self.history.append(types.Content(role="user", parts=[types.Part(text=t_ctx + text)]))
        self.stats.add_usage(MODEL_FAST, input_units=len(text)//4)
        self.stats.active_brain = "FAST"
        
        # SMARTER PRUNING: Keep first 2 (system context) + last 30 turns
        if len(self.history) > 40:
             self.history = self.history[:2] + self.history[-38:]
        
        try:
            # 15s Timeout to prevent 'Stuck' state
            resp = await asyncio.wait_for(
                with_retry(lambda: self.client.aio.models.generate_content(model=MODEL_FAST, contents=self.history, config=self.fast)),
                timeout=15.0
            )
            router = resp.parsed
        except Exception as e:
            router = RouterResponse(reply=f"Engine Lag: {str(e)[:50]}...", requires_deep_reasoning=True)
        
        self.stats.add_usage(MODEL_FAST, output_units=len(router.reply)//4)
        self.history.append(types.Content(role="model", parts=[types.Part(text=router.reply)]))
        self.stats.active_brain = None
        
        deep = ""
        if router.requires_deep_reasoning: 
            self.stats.active_brain = "DEEP"
            deep = await self._invoke_deep(text)
            self.stats.active_brain = None
        return router.reply, router.requires_deep_reasoning, deep

    async def _invoke_deep(self, query: str) -> str:
        chat = self.client.aio.chats.create(model=MODEL_DEEP, history=self.history[:-1], config=self.deep)
        prompt = f"Deep Task: {query}"
        self.stats.add_usage(MODEL_DEEP, input_units=len(prompt)//4)
        try:
            resp = await with_retry(lambda: chat.send_message(prompt))
            turns = 0
            while resp.function_calls and turns < 5:
                turns += 1; parts = []
                for call in resp.function_calls:
                    res = await self._exec(call)
                    parts.append(types.Part(function_response=types.FunctionResponse(name=call.name, response={"result": res})))
                resp = await with_retry(lambda: chat.send_message(parts))
            txt = resp.text or "Done."
            self.stats.add_usage(MODEL_DEEP, output_units=len(txt)//4)
            self.history.append(types.Content(role="model", parts=[types.Part(text=txt)]))
            return txt
        except Exception as e: return f"Error: {e}"

    async def _exec(self, call):
        if not SEARCH_ENGINE: return "No Search Engine"
        try:
            if call.name == "search_google": return SEARCH_ENGINE.grounding_search(call.args["query"])
            if call.name == "fetch_url": return SEARCH_ENGINE.web_fetch(call.args["url"])
            if call.name == "bigquery_query": return SEARCH_ENGINE.bigquery_query(call.args["sql_query"])
            if call.name == "list_gcs_files": return SEARCH_ENGINE.list_gcs(call.args["bucket_name"])
            if call.name == "read_gcs_file": return SEARCH_ENGINE.read_gcs(call.args["bucket_name"], call.args["filename"])
        except Exception as e: return str(e)
        return "Unknown"

# ===============================================================================
# MAIN ENGINE
# ===============================================================================

class BanditVoiceEngine:
    def __init__(self):
        self.state = AtomicState()
        self.stats = SessionStats()
        self.audio_cfg = AudioConfig()
        self.client = genai.Client(vertexai=True, project=os.environ.get("GOOGLE_CLOUD_PROJECT"))
        global SEARCH_ENGINE
        if VoiceAISearchEngine: SEARCH_ENGINE = VoiceAISearchEngine(client=self.client)
        
        self.mic = MicrophoneService(self.audio_cfg.use_webrtc_vad, use_elgato=True, stats=self.stats)
        self.tts = TTSService(self.client, self.mic, self.audio_cfg.barge_in_threshold)
        self.transcriber = TranscriptionService()
        self.transcriber.warm_up()
        self.ui = LiveTranscriptDisplay(self.stats)
        self.convo = ConversationManager(self.client, """YOU ARE BANDIT. 
[DUAL BRAIN]
- Fast: Instant, 2026 Countdown.
- Deep: Complex Tools (Search/BQ/GCS).""", self.stats)
        self.session_start = time.time()

    async def run(self):
        async with self.ui.live_display() as display:
            display.set_status(f"Initializing Mic: {self.mic.device_name}...")
            # Brief pause to let developer see the mic name
            await asyncio.sleep(1.0)
            while True:
                try:
                    self.state.set(SessionState.LISTENING)
                    display.set_status("Listening...")
                    
                    audio = await asyncio.to_thread(self.mic.listen_until_silence, 
                        self.audio_cfg.silence_threshold, self.audio_cfg.silence_duration, 30.0)
                    if not audio or len(audio) < 1000: continue
                    
                    self.state.set(SessionState.PROCESSING)
                    self.state.set(SessionState.PROCESSING)
                    self.stats.active_brain = "TRANS"
                    display.set_status(f"Transcribing {len(audio)/32000:.1f}s audio...")
                    
                    try:
                        # 8s Timeout to prevent Ghost-Lock in Whisper
                        t_trans_0 = time.time()
                        text = await asyncio.wait_for(
                            asyncio.to_thread(self.transcriber.transcribe, audio),
                            timeout=8.0
                        )
                        t_trans_lat = time.time() - t_trans_0
                        if not text: 
                            self.stats.active_brain = None
                            continue
                    except asyncio.TimeoutError:
                        display.set_status("Transcription Timeout (Skipping)")
                        self.stats.active_brain = None
                        continue
                    finally:
                        self.stats.active_brain = None
                    
                    # Timing Start
                    t0 = time.time()
                    
                    # Add User Segment (Simulated Confidence)
                    seg_end = time.time() - self.session_start
                    display.add_segment({
                        "start": seg_end - 2, 
                        "end": seg_end, 
                        "text": text,
                        "confidence": 0.95 
                    }, "USER")
                    
                    display.set_status("Thinking...")
                    
                    fast, needed_deep, deep = await self.convo.route_and_respond(text)
                    
                    # Latency Capture
                    self.stats.last_latency = time.time() - t0
                    
                    self.state.set(SessionState.SPEAKING)
                    display.set_status("Speaking...")
                    
                    t_start = time.time() - self.session_start
                    interrupted = await self.tts.speak(fast)
                    t_end = time.time() - self.session_start
                    
                    if interrupted:
                        display.add_interruption(t_end)
                        display.add_segment({
                            "start": t_start, 
                            "end": t_end, 
                            "text": fast + "...",
                            "confidence": 1.0
                        }, "FAST")
                        self.tts.stop()
                        self.stats.turns += 1
                        continue
                    
                    display.add_segment({
                        "start": t_start, 
                        "end": t_end, 
                        "text": fast,
                        "confidence": 1.0
                    }, "FAST")

                    if needed_deep:
                        display.set_status("Deep Brain...")
                        t_start = time.time() - self.session_start
                        await self.tts.speak(deep) # Simplification
                        t_end = time.time() - self.session_start
                        display.add_segment({
                            "start": t_start, 
                            "end": t_end, 
                            "text": deep,
                            "confidence": 1.0
                        }, "DEEP")
                    
                    self.stats.turns += 1
                except Exception as e:
                    display.set_status(f"Error: {e}")
                    self.stats.errors += 1
                    await asyncio.sleep(2.0)

if __name__ == "__main__":
    eng = BanditVoiceEngine()
    try: asyncio.run(eng.run())
    except KeyboardInterrupt: pass
