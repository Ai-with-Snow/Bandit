"""Deploy helper for running Gemini agents from Google Cloud Shell or local CLI.

Resolves credentials (API key vs. Vertex AI), picks a Gemini model, and runs a
smoke prompt so you can confirm access to Google GenAI.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from typing import Optional

import agents

DEFAULT_LOCATION = (
    os.getenv("GENAI_LOCATION")
    or os.getenv("GOOGLE_GENAI_LOCATION")
    or "us-central1"
)


def in_cloud_shell() -> bool:
    """Check whether the script is running inside Cloud Shell."""
    return os.getenv("CLOUD_SHELL", "").lower() == "true"


def resolve_project(explicit: Optional[str]) -> Optional[str]:
    """Pick a project from CLI, environment, or gcloud config."""
    if explicit:
        return explicit

    for env_var in ("GENAI_PROJECT", "GOOGLE_CLOUD_PROJECT", "GCLOUD_PROJECT"):
        value = os.getenv(env_var)
        if value:
            return value

    gcloud = shutil.which("gcloud")
    if gcloud:
        try:
            output = subprocess.check_output([gcloud, "config", "get-value", "project"], text=True)
            project = output.strip()
            if project and project.lower() != "(unset)":
                return project
        except subprocess.CalledProcessError:
            return None

    return None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Configure and smoke-test Google GenAI from Cloud Shell.",
    )
    parser.add_argument(
        "--project",
        help="Google Cloud project for Vertex AI (used when GOOGLE_API_KEY is missing).",
    )
    parser.add_argument(
        "--location",
        default=DEFAULT_LOCATION,
        help=f"Vertex AI region (default: {DEFAULT_LOCATION}).",
    )
    parser.add_argument(
        "--model",
        choices=agents.SUPPORTED_MODELS,
        default=agents.DEFAULT_MODEL,
        help=f"Gemini model to target (default: {agents.DEFAULT_MODEL}).",
    )
    parser.add_argument(
        "--prompt",
        default="Ping from LMSIFY Cloud Shell.",
        help="Prompt to send for the smoke test.",
    )
    parser.add_argument(
        "--system",
        help="Optional path to agent instructions for system_instruction.",
    )
    parser.add_argument(
        "--api-key",
        dest="api_key",
        default=os.getenv("GOOGLE_API_KEY"),
        help="Google AI Studio API key. If omitted, Vertex AI is used.",
    )
    parser.add_argument(
        "--vertex",
        action="store_true",
        help="Force Vertex AI even if an API key is present.",
    )
    parser.add_argument(
        "--stream",
        action="store_true",
        help="Stream the response for the smoke test.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print resolved settings without calling the model.",
    )
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="List supported models and exit.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.list_models:
        print("Supported models:")
        for model in agents.SUPPORTED_MODELS:
            print(f"- {model}")
        return

    project = resolve_project(args.project)
    settings = agents.GenAISettings(
        model=args.model,
        project=project,
        location=args.location or DEFAULT_LOCATION,
        system_instruction=agents.load_text(args.system),
        api_key=args.api_key,
    )

    print("[deploy] Environment summary:")
    print(f"- Cloud Shell: {'yes' if in_cloud_shell() else 'no'}")
    print(f"- Mode: Vertex AI (LangChain)")
    print(f"- Model: {settings.model}")
    print(f"- Project: {settings.project or 'n/a'}")
    print(f"- Location: {settings.location}")
    print(f"- API key fallback: {'yes' if args.api_key else 'no'}")

    if not project:
        parser.error("Vertex AI requested but no project found. Set --project or GOOGLE_CLOUD_PROJECT.")

    if args.dry_run:
        return

    try:
        response = agents.run_prompt(args.prompt, settings, stream=args.stream)
        if response:
            print(response)
    except Exception as exc:  # pragma: no cover - CLI surface
        print(f"[deploy] Error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
