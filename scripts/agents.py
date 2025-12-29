"""CLI helper to run LMSIFY agents against Google GenAI Gemini models via LangChain.

Supports Vertex AI credentials and integrates with LangChain for advanced agent capabilities.
Defaults to `gemini-3-flash-preview` (1M context, free tier).
"""

from __future__ import annotations

import argparse
import os
import sys
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence

from google.oauth2 import service_account
from langchain_google_vertexai import ChatVertexAI
from langchain_core.messages import HumanMessage, SystemMessage

# Gemini 3 and 2.5 Models - All with 1M token context
SUPPORTED_MODELS = [
    # Gemini 3 (Latest)
    "gemini-3-flash-preview",
    "gemini-3-pro-preview",
    "gemini-3-pro-image-preview",
    # Gemini 2.5
    "gemini-2.5-pro",
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
]

DEFAULT_MODEL = "gemini-3-flash-preview"  # Free tier, 1M context, $0.50/$3.00 per 1M tokens
DEFAULT_LOCATION = (
    os.getenv("GENAI_LOCATION")
    or os.getenv("GOOGLE_GENAI_LOCATION")
    or "us-central1"
)


@dataclass
class GenAISettings:
    """Runtime configuration for the GenAI client."""

    model: str = DEFAULT_MODEL
    project: Optional[str] = None
    location: str = DEFAULT_LOCATION
    system_instruction: Optional[str] = None
    api_key: Optional[str] = None


def _resolve_location(model: str, requested_location: str) -> str:
    """Route Gemini 3 models to the global endpoint."""
    if model.startswith("gemini-3-"):
        return "global"
    return requested_location


def _load_credentials_from_env():
    """Create credentials from GOOGLE_APPLICATION_CREDENTIALS_JSON if provided."""
    json_blob = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
    if not json_blob:
        return None
    try:
        info = json.loads(json_blob)
        scopes = ["https://www.googleapis.com/auth/cloud-platform"]
        return service_account.Credentials.from_service_account_info(info, scopes=scopes)
    except Exception as exc:  # pragma: no cover - config path
        raise ValueError("Invalid GOOGLE_APPLICATION_CREDENTIALS_JSON value") from exc


def load_text(path: Optional[str]) -> Optional[str]:
    """Return file contents if a path is provided."""
    if not path:
        return None
    return Path(path).read_text(encoding="utf-8").strip()


def create_client(settings: GenAISettings) -> ChatVertexAI:
    """Create a LangChain ChatVertexAI client."""
    project = settings.project or os.getenv("GENAI_PROJECT") or os.getenv("GOOGLE_CLOUD_PROJECT")
    
    if not project:
        raise ValueError("Vertex AI requires a project ID. Set --project or GOOGLE_CLOUD_PROJECT.")

    location = _resolve_location(settings.model, settings.location)
    credentials = _load_credentials_from_env()

    return ChatVertexAI(
        model_name=settings.model,
        project=project,
        location=location,
        credentials=credentials,
        temperature=0.7,
        max_output_tokens=2048,
    )


def run_prompt(prompt: str, settings: GenAISettings, stream: bool = False) -> str:
    """Send a prompt to the chosen Gemini model via LangChain."""
    if not prompt:
        raise ValueError("A prompt is required.")

    fallback_key = settings.api_key or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    last_error: Optional[Exception] = None

    # Vertex first
    try:
        chat = create_client(settings)
        
        messages = []
        if settings.system_instruction:
            messages.append(SystemMessage(content=settings.system_instruction))
        messages.append(HumanMessage(content=prompt))

        if stream:
            print("Streaming response...", flush=True)
            full_response = ""
            for chunk in chat.stream(messages):
                if chunk.content:
                    print(chunk.content, end="", flush=True)
                    full_response += chunk.content
            print()  # newline after streamed output
            return full_response

        response = chat.invoke(messages)
        return response.content
    except Exception as exc:
        last_error = exc
        if not fallback_key:
            raise

    # API key fallback (google-genai)
    try:
        from google import genai

        client = genai.Client(api_key=fallback_key)
        contents = prompt if not settings.system_instruction else f"{settings.system_instruction}\n\n{prompt}"

        if stream:
            print("Streaming response (API key fallback)...", flush=True)
            full_response = ""
            for chunk in client.models.generate_content_stream(
                model=settings.model,
                contents=contents,
            ):
                if chunk.text:
                    print(chunk.text, end="", flush=True)
                    full_response += chunk.text
            print()
            return full_response

        response = client.models.generate_content(
            model=settings.model,
            contents=contents,
        )
        return response.text
    except Exception as fallback_exc:  # pragma: no cover - resilience path
        if last_error:
            raise RuntimeError(f"Vertex AI failed ({last_error}); API key fallback also failed ({fallback_exc})")
        raise


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a prompt through Google GenAI (Gemini) via LangChain."
    )
    parser.add_argument(
        "prompt",
        nargs="?",
        help="Prompt text. If omitted, reads from stdin.",
    )
    parser.add_argument(
        "--prompt-file",
        help="Path to a file containing the prompt text.",
    )
    parser.add_argument(
        "--system",
        help="Optional path to agent instructions (sent as system_instruction).",
    )
    parser.add_argument(
        "--model",
        choices=SUPPORTED_MODELS,
        default=DEFAULT_MODEL,
        help=f"Gemini model to target (default: {DEFAULT_MODEL}).",
    )
    parser.add_argument(
        "--project",
        help="Google Cloud project ID for Vertex AI usage.",
    )
    parser.add_argument(
        "--location",
        default=DEFAULT_LOCATION,
        help=f"Vertex AI region to use (default: {DEFAULT_LOCATION}).",
    )
    parser.add_argument(
        "--stream",
        action="store_true",
        help="Stream the response instead of waiting for completion.",
    )
    return parser.parse_args(argv)


def resolve_prompt(args: argparse.Namespace) -> str:
    """Pick the prompt from CLI, file, or stdin."""
    if args.prompt_file:
        return Path(args.prompt_file).read_text(encoding="utf-8").strip()

    if args.prompt:
        return args.prompt

    if not sys.stdin.isatty():
        stdin_value = sys.stdin.read().strip()
        if stdin_value:
            return stdin_value

    raise SystemExit("Provide a prompt argument, --prompt-file, or pipe text to stdin.")


def main(argv: Sequence[str] | None = None) -> None:
    args = parse_args(argv)

    prompt = resolve_prompt(args)
    system_instruction = load_text(args.system)

    settings = GenAISettings(
        model=args.model,
        project=args.project,
        location=args.location,
        system_instruction=system_instruction,
    )

    try:
        output = run_prompt(prompt, settings, stream=args.stream)
        if output and not args.stream:
            print(output)
    except Exception as exc:  # pragma: no cover - CLI surface
        print(f"[agents] Error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
