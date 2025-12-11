"""Advanced prompting techniques for Bandit.

Based on DAV1D's prompting patterns:
- Tree of Thought (ToT): Multi-path brainstorming and synthesis
- Battle of Bots: Adversarial validation through competing drafts
- Prompt Optimizer: Meta-prompting to enhance vague prompts
"""

import os
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()


def _get_genai_client():
    """Get a google.genai client for prompting."""
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


def tree_of_thought(task: str, model_key: str = "deep") -> str:
    """Tree of Thought: Multi-path brainstorming and synthesis.
    
    Generates multiple strategic approaches and synthesizes the best path.
    
    Args:
        task: The problem or task to analyze
        model_key: Model tier (deep recommended for complex reasoning)
    
    Returns:
        Synthesized "Golden Path" solution
    """
    models = {
        "lite": "gemini-2.5-flash-lite",
        "flash": "gemini-2.5-flash",
        "balanced": "gemini-2.5-pro",
        "deep": "gemini-3-pro-preview",
    }
    model = models.get(model_key, "gemini-2.5-pro")
    
    console.print(Panel(
        f"[bold]Task:[/bold] {task}\n[dim]Using: {model}[/dim]",
        title="[bold green]🌳 TREE OF THOUGHT[/bold green]",
        border_style="green"
    ))
    console.print("[dim]Generating multiple strategic paths...[/dim]\n")
    
    prompt = f"""Using Tree of Thought (TOT) methodology:

TASK: {task}

Step 1 - BRAINSTORM: Generate 3 distinct approaches:
- **Approach A (Conservative/Safe):** The low-risk, proven path
- **Approach B (Aggressive/Fast):** The high-speed, high-reward path
- **Approach C (Creative/Unconventional):** The unexpected, innovative path

Step 2 - EVALUATE: For each approach, analyze:
- Strengths (what makes it work)
- Weaknesses (what could fail)
- Success likelihood (1-10)
- Time/resource requirements

Step 3 - SYNTHESIZE: Combine the best elements into a **"Golden Path"** solution that:
- Minimizes weaknesses from each approach
- Maximizes combined strengths
- Provides a clear action plan

Present each step clearly with headers, then give a final recommendation with specific action items.
"""
    
    try:
        result = _generate(prompt, model)
        console.print(Panel(
            Markdown(result),
            title="[green]TOT RESULT[/green]",
            border_style="green"
        ))
        return result
    except Exception as e:
        error = f"Tree of Thought failed: {e}"
        console.print(f"[red]{error}[/red]")
        return error


def battle_of_bots(task: str, model_key: str = "deep") -> str:
    """Battle of Bots: Adversarial validation through competing drafts.
    
    Generates competing approaches, critiques them brutally, then synthesizes.
    
    Args:
        task: The task to battle over
        model_key: Model tier (deep recommended for thorough critique)
    
    Returns:
        The "Golden Version" after adversarial refinement
    """
    models = {
        "lite": "gemini-2.5-flash-lite",
        "flash": "gemini-2.5-flash",
        "balanced": "gemini-2.5-pro",
        "deep": "gemini-3-pro-preview",
    }
    model = models.get(model_key, "gemini-2.5-pro")
    
    console.print(Panel(
        f"[bold]Task:[/bold] {task}\n[dim]Using: {model}[/dim]",
        title="[bold gold]⚔️ BATTLE OF THE BOTS[/bold gold]",
        border_style="gold"
    ))
    
    prompt = f"""Adversarial Validation Protocol - Battle of the Bots:

TASK: {task}

## ROUND 1 - COMPETING DRAFTS
Generate TWO distinct versions:

### [ICE WIRE VERSION]
Analytical, data-focused, methodical approach.
Focus on: precision, risk mitigation, proven patterns.

### [CIPHER VERSION]
Creative, unconventional, bold approach.
Focus on: innovation, opportunity, breaking patterns.

---

## ROUND 2 - BRUTAL CRITIQUE
As **THE CRITIC** (harsh, brutally honest):
- Roast BOTH versions mercilessly
- Point out every weakness, flaw, and soft spot
- What would Snow be disappointed by in each?
- What's lazy or obvious about each approach?

---

## ROUND 3 - SYNTHESIS
Create ONE final **[GOLDEN VERSION]** that:
- Addresses ALL critique points
- Merges the best elements from both
- Eliminates the weaknesses identified
- Is something Snow would genuinely approve of

Show all three rounds clearly with headers.
"""
    
    console.print("[bold red][ROUND 1][/bold red] Generating competing drafts...\n")
    
    try:
        result = _generate(prompt, model)
        console.print(Panel(
            Markdown(result),
            title="[gold]BATTLE RESULT[/gold]",
            border_style="gold"
        ))
        console.print(Panel(
            "[dim]Adversarial validation complete. Golden version extracted.[/dim]",
            title="[bold gold]⚔️ BATTLE CONCLUDED[/bold gold]",
            border_style="gold"
        ))
        return result
    except Exception as e:
        error = f"Battle of Bots failed: {e}"
        console.print(f"[red]{error}[/red]")
        return error


def optimize_prompt(raw_prompt: str, model_key: str = "balanced") -> str:
    """Prompt Optimizer: Meta-prompting to enhance vague prompts.
    
    Takes a rough prompt and transforms it into a highly effective one.
    
    Args:
        raw_prompt: The original, rough prompt to optimize
        model_key: Model tier to use
    
    Returns:
        Enhanced prompt with explanation of improvements
    """
    models = {
        "lite": "gemini-2.5-flash-lite",
        "flash": "gemini-2.5-flash",
        "balanced": "gemini-2.5-pro",
        "deep": "gemini-3-pro-preview",
    }
    model = models.get(model_key, "gemini-2.5-pro")
    
    console.print(Panel(
        f"[bold]Original:[/bold] {raw_prompt}\n[dim]Using: {model}[/dim]",
        title="[bold cyan]✨ PROMPT OPTIMIZER[/bold cyan]",
        border_style="cyan"
    ))
    console.print("[dim]Enhancing your prompt...[/dim]\n")
    
    prompt = f"""You are an expert prompt engineer. Transform this rough prompt into a highly effective one.

ROUGH PROMPT: "{raw_prompt}"

Enhance by adding:
1. **Clear PERSONA** - Who should answer? What expertise do they have?
2. **Essential CONTEXT** - What background info is needed?
3. **OUTPUT REQUIREMENTS** - Format, length, tone, structure
4. **FEW-SHOT EXAMPLES** - 2-3 examples if applicable
5. **CHAIN OF THOUGHT** - Step-by-step thinking instructions

Return in this exact format:

---
## OPTIMIZED PROMPT

[Your enhanced prompt here - ready to copy/paste]

---
## IMPROVEMENTS MADE

[Brief bullet list of what was added/improved]

---
## EXPECTED QUALITY BOOST

[One sentence on why this will work better]
"""
    
    try:
        result = _generate(prompt, model)
        console.print(Panel(
            Markdown(result),
            title="[cyan]OPTIMIZED[/cyan]",
            border_style="cyan"
        ))
        return result
    except Exception as e:
        error = f"Prompt optimization failed: {e}"
        console.print(f"[red]{error}[/red]")
        return error


if __name__ == "__main__":
    # Test the prompting techniques
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python prompting.py [tot|battle|optimize] <task>")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    task = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "Example task"
    
    if command == "tot":
        tree_of_thought(task)
    elif command == "battle":
        battle_of_bots(task)
    elif command == "optimize":
        optimize_prompt(task)
    else:
        print(f"Unknown command: {command}")
