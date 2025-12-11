"""Multi-agent council for Bandit HQ.

Based on DAV1D's council pattern: multiple agents discuss and synthesize.
Council members:
- BANDIT: HQ Operator - synthesizes and makes final decisions
- ICE WIRE: Operations Signalist - analytical, data-focused
- CIPHER: Deep Analyst - creative, unconventional approaches
"""

import os
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()

# Agent profiles based on existing Bandit/Ice Wire docs + new Cipher
BANDIT_PROFILE = """You are Bandit, the HQ Operator for LMSIFY.

[IDENTITY]
- System Operator and central coordinator for all HQ operations
- Translates directives from Goddexx Snow into actionable briefs
- Safeguards cross-agent coordination with transparency

[PERSONALITY]
- Calm authority - "Stillness is the vibe"
- Precise technical cues with confident, minimal prose
- No filler, just signal

[ROLE IN COUNCIL]
- You are the SYNTHESIZER - you make the final call
- Acknowledge your advisors' perspectives
- State your decision clearly and give the directive
"""

ICEWIRE_PROFILE = """You are Ice Wire, Operations Signalist and Bandit's sidekick.

[IDENTITY]  
- Amplifies Bandit's directives across HQ
- Maintains clarity inside HQ so every room knows what assets exist
- Watches for gaps and nudges the right agents before issues escalate

[PERSONALITY]
- Signal-operator energy - short transmissions, confident handoffs, zero fluff
- Data-backed and thorough
- Crisp and methodical

[ROLE IN COUNCIL]
- You are the ANALYST - focus on data, patterns, and risk
- What are the logical constraints?
- What does the data suggest?
- End with: CONFIRMED / UNCERTAIN / INVESTIGATE
"""

CIPHER_PROFILE = """You are Cipher, Deep Analyst for Bandit HQ.

[IDENTITY]
- Strategic advisor who sees patterns others miss
- Questions obvious approaches
- Connects unrelated concepts for breakthrough solutions

[PERSONALITY]
- Unconventional thinker, outside the box
- Energetic, optimistic, possibility-focused
- Bold but grounded

[ROLE IN COUNCIL]
- You are the CREATIVE - explore unconventional paths
- What's the bold move here?
- What opportunities are being missed?
- End with: EXPLORE / REFINE / ABANDON
"""


def _get_genai_client():
    """Get a google.genai client for council queries."""
    from google import genai
    from google.genai.types import HttpOptions
    
    project = os.getenv("GOOGLE_CLOUD_PROJECT", "project-5f169828-6f8d-450b-923")
    location = os.getenv("BANDIT_LOCATION", "us-central1")
    
    return genai.Client(
        vertexai=True,
        project=project,
        location=location,
        http_options=HttpOptions(api_version="v1")
    )


def _generate(prompt: str, model: str = "gemini-2.5-pro") -> str:
    """Generate content using google.genai."""
    client = _get_genai_client()
    
    response = client.models.generate_content(
        model=model,
        contents=prompt
    )
    
    return response.text if hasattr(response, 'text') else str(response)


def run_council(query: str, model_key: str = "balanced") -> str:
    """Multi-agent council: Ice Wire analyzes, Cipher explores, Bandit synthesizes.
    
    Args:
        query: The task or question for the council
        model_key: Model tier to use (balanced = 2.5 Pro, deep = 3.0 Pro)
    
    Returns:
        Bandit's synthesized final decision
    """
    # Map model keys to actual model names
    models = {
        "lite": "gemini-2.5-flash-lite",
        "flash": "gemini-2.5-flash",
        "balanced": "gemini-2.5-pro",
        "deep": "gemini-3-pro-preview",
    }
    model = models.get(model_key, "gemini-2.5-pro")
    
    console.print(Panel(
        f"[bold]Task:[/bold] {query}\n[dim]Model: {model}[/dim]",
        title="[bold gold]⚔️ COUNCIL INITIATED[/bold gold]",
        border_style="gold"
    ))
    
    # ICE WIRE's analytical take
    console.print("\n[bold green][ICE WIRE][/bold green] Running signal analysis...")
    icewire_prompt = f"""{ICEWIRE_PROFILE}

TASK: {query}

Analyze:
1. What data/patterns are relevant?
2. What's the logical approach?
3. What are the risks/constraints?

Respond in 2-4 sentences. Be data-focused. End with CONFIRMED/UNCERTAIN/INVESTIGATE.
"""
    
    try:
        icewire_response = _generate(icewire_prompt, model)
        console.print(Panel(
            Markdown(icewire_response),
            title="[green]ICE WIRE[/green]",
            border_style="green"
        ))
    except Exception as e:
        icewire_response = f"[Analysis error: {e}]"
        console.print(f"[red]ICE WIRE Error: {e}[/red]")
    
    # CIPHER's creative take
    console.print("\n[bold purple][CIPHER][/bold purple] Exploring possibilities...")
    cipher_prompt = f"""{CIPHER_PROFILE}

TASK: {query}
ICE WIRE's Analysis: {icewire_response}

Think creatively:
1. What unconventional approaches exist?
2. What opportunities is ICE WIRE missing?
3. What's the bold move here?

Respond in 2-4 sentences. Be creative. End with EXPLORE/REFINE/ABANDON.
"""
    
    try:
        cipher_response = _generate(cipher_prompt, model)
        console.print(Panel(
            Markdown(cipher_response),
            title="[purple]CIPHER[/purple]",
            border_style="purple"
        ))
    except Exception as e:
        cipher_response = f"[Creative error: {e}]"
        console.print(f"[red]CIPHER Error: {e}[/red]")
    
    # BANDIT synthesizes
    console.print("\n[bold magenta][BANDIT][/bold magenta] Synthesizing...")
    bandit_prompt = f"""{BANDIT_PROFILE}

You're the HQ Operator. Your advisors have weighed in. Make the call.

TASK: {query}
ICE WIRE's Analysis: {icewire_response}
CIPHER's Creative Take: {cipher_response}

Synthesize:
1. Where do they align?
2. Where do they diverge?
3. What's the optimal path forward?

Respond in 3-5 sentences as Bandit. Acknowledge perspectives, state your decision, give the directive.
"""
    
    try:
        final_response = _generate(bandit_prompt, model)
        console.print(Panel(
            Markdown(final_response),
            title="[bold magenta]BANDIT - FINAL DECISION[/bold magenta]",
            border_style="magenta"
        ))
    except Exception as e:
        final_response = f"Council synthesis error: {e}"
        console.print(f"[red]BANDIT Error: {e}[/red]")
    
    console.print(Panel(
        "[dim]All perspectives considered. Decision logged.[/dim]",
        title="[bold gold]⚔️ COUNCIL CONCLUDED[/bold gold]",
        border_style="gold"
    ))
    
    return final_response


if __name__ == "__main__":
    # Test the council
    import sys
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "How should we prioritize HQ tasks?"
    run_council(query)
