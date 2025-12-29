#!/usr/bin/env python3
"""
Bandit Voice Agent - Listen & Talk using Gemini 2.5 Flash-Lite (Fastest & Cheapest)
Listens to user via microphone, processes with Gemini, responds via TTS
"""

import os
import io
import wave
import sys

# Configuration
API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
MODEL_CHAT = "gemini-2.5-flash-lite"  # Fastest, cheapest for chat
MODEL_TTS = "gemini-2.5-flash-lite-preview-tts"  # Fastest, cheapest for TTS
BANDIT_VOICE = "Charon"  # Informative male voice (Bandit's default)

# Audio playback configuration
CHUNK = 1024
SAMPLE_RATE = 24000
CHANNELS = 1
SAMPLE_WIDTH = 2  # 16-bit PCM


def check_dependencies():
    """Check if required packages are installed."""
    missing = []
    optional_missing = []
    
    try:
        from google import genai
    except ImportError:
        missing.append("google-genai")
    try:
        import pyaudio
    except ImportError:
        missing.append("pyaudio")
    try:
        import speech_recognition
    except ImportError:
        missing.append("SpeechRecognition")
    
    # Optional: faster-whisper for local transcription
    try:
        from faster_whisper import WhisperModel
        print("✅ faster-whisper available (local transcription)")
    except ImportError:
        optional_missing.append("faster-whisper")
        print("ℹ️  faster-whisper not installed (using Google Speech)")
    
    if missing:
        print(f"❌ Missing packages: {', '.join(missing)}")
        print(f"Install with: pip install {' '.join(missing)}")
        return False
    
    if optional_missing:
        print(f"💡 Optional: pip install {' '.join(optional_missing)}")
    
    return True


def initialize_client():
    """Initialize Gemini client - supports both API key and Vertex AI auth."""
    from google import genai
    
    # Option 1: API key (if set)
    if API_KEY:
        print("🔑 Using API key authentication")
        return genai.Client(api_key=API_KEY)
    
    # Option 2: Vertex AI with gcloud auth (no API key needed!)
    project = os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("GCP_PROJECT")
    if project:
        print(f"☁️  Using Vertex AI authentication (project: {project})")
        return genai.Client(vertexai=True, project=project, location="global")
    
    # Fallback: Try Vertex AI with default project
    try:
        print("☁️  Using Vertex AI with default credentials")
        return genai.Client(vertexai=True, location="global")
    except Exception as e:
        print(f"❌ Auth error: {e}")
        print("Set GEMINI_API_KEY or run: gcloud auth application-default login")
        return None


def listen_to_user():
    """Capture audio from microphone and convert to text.
    Uses faster-whisper for local transcription (faster, offline).
    Falls back to Google Speech Recognition if faster-whisper not available.
    """
    import speech_recognition as sr
    recognizer = sr.Recognizer()
    
    with sr.Microphone() as source:
        print("🎤 Listening... (speak now)")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=15)
            print("🔄 Processing speech...")
            
            # Try faster-whisper first (local, fast, offline)
            try:
                from faster_whisper import WhisperModel
                import numpy as np
                import tempfile
                import wave
                
                # Save audio to temp file for faster-whisper
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                    wav_data = audio.get_wav_data()
                    f.write(wav_data)
                    temp_path = f.name
                
                # Load model (uses GPU if available, otherwise CPU)
                # small model is good balance of speed/accuracy
                model = WhisperModel("small", device="auto", compute_type="auto")
                
                # Transcribe
                segments, info = model.transcribe(temp_path, beam_size=5)
                text = " ".join([segment.text for segment in segments]).strip()
                
                # Cleanup
                import os
                os.unlink(temp_path)
                
                if text:
                    print(f"📝 You said (whisper): {text}")
                    return text
                    
            except ImportError:
                pass  # Fall back to Google
            except Exception as e:
                print(f"⚠️ Whisper error, using Google: {e}")
            
            # Fallback: Google Speech Recognition (online)
            text = recognizer.recognize_google(audio)
            print(f"📝 You said (google): {text}")
            return text
            
        except sr.WaitTimeoutError:
            print("⏱️ No speech detected. Please try again.")
            return None
        except sr.UnknownValueError:
            print("❌ Could not understand audio. Please try again.")
            return None
        except sr.RequestError as e:
            print(f"❌ Speech recognition error: {e}")
            return None


def chat_with_gemini(client, user_input, conversation_history):
    """Send user input to Gemini and get response"""
    try:
        # Add user message to history
        conversation_history.append({
            "role": "user",
            "parts": [{"text": user_input}]
        })
        
        # Generate response
        response = client.models.generate_content(
            model=MODEL_CHAT,
            contents=conversation_history
        )
        
        assistant_response = response.text
        
        # Add assistant response to history
        conversation_history.append({
            "role": "model", 
            "parts": [{"text": assistant_response}]
        })
        
        print(f"🤖 Bandit: {assistant_response}")
        return assistant_response
        
    except Exception as e:
        print(f"❌ Chat error: {e}")
        return None


def speak_response(client, text, voice=BANDIT_VOICE):
    """Convert text to speech and play audio"""
    try:
        from google.genai import types
        
        # Generate TTS with Gemini 2.5 Flash-Lite (cheapest & fastest)
        response = client.models.generate_content(
            model=MODEL_TTS,
            contents=text,
            config=types.GenerateContentConfig(
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name=voice
                        )
                    )
                ),
                response_modalities=["AUDIO"],
            )
        )
        
        # Extract audio data from response
        audio_data = None
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'inline_data') and part.inline_data:
                audio_data = part.inline_data.data
                break
        
        if not audio_data:
            print("⚠️ No audio data received")
            return
        
        # Play audio using PyAudio
        print("🔊 Playing response...")
        play_audio(audio_data)
        
    except Exception as e:
        print(f"❌ TTS error: {e}")


def play_audio(pcm_data):
    """Play PCM audio data through speakers"""
    import pyaudio
    try:
        p = pyaudio.PyAudio()
        
        stream = p.open(
            format=p.get_format_from_width(SAMPLE_WIDTH),
            channels=CHANNELS,
            rate=SAMPLE_RATE,
            output=True
        )
        
        stream.write(pcm_data)
        stream.stop_stream()
        stream.close()
        p.terminate()
        
    except Exception as e:
        print(f"❌ Audio playback error: {e}")


def save_audio_to_file(pcm_data, filename="bandit_audio.wav"):
    """Optional: Save audio to WAV file"""
    try:
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(SAMPLE_WIDTH)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(pcm_data)
        print(f"💾 Audio saved to {filename}")
    except Exception as e:
        print(f"❌ Save error: {e}")


def main():
    """Main voice agent loop"""
    print("=" * 50)
    print("🎙️  BANDIT VOICE AGENT")
    print("=" * 50)
    print(f"Chat Model: {MODEL_CHAT}")
    print(f"TTS Model:  {MODEL_TTS}")
    print(f"Voice:      {BANDIT_VOICE}")
    print("Say 'exit', 'quit', or 'bye' to end\n")
    
    if not check_dependencies():
        return
    
    # Initialize client (supports API key OR gcloud auth)
    client = initialize_client()
    if not client:
        return
    
    conversation_history = []
    
    # Bandit system prompt
    conversation_history.append({
        "role": "user",
        "parts": [{"text": "You are Bandit, an AI assistant created by LMSIFY. You're helpful, knowledgeable, and slightly playful. Keep responses concise and conversational for voice output."}]
    })
    conversation_history.append({
        "role": "model",
        "parts": [{"text": "Hey! I'm Bandit, your AI assistant. What's on your mind?"}]
    })
    
    # Main conversation loop
    while True:
        # Listen to user
        user_input = listen_to_user()
        
        if not user_input:
            continue
        
        # Check for exit commands
        if user_input.lower() in ["exit", "quit", "bye", "goodbye", "stop"]:
            print("👋 Goodbye!")
            speak_response(client, "Peace out! Catch you later!")
            break
        
        # Get AI response
        ai_response = chat_with_gemini(client, user_input, conversation_history)
        
        if ai_response:
            # Speak response
            speak_response(client, ai_response)
        
        print("\n" + "-" * 50 + "\n")


if __name__ == "__main__":
    main()
