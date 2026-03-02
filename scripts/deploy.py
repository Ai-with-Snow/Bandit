"""Interactive Deploy helper for Bandit and LMSIFY HQ.

Provides a rich terminal UI with 'buttons' (selectable options) for 
deploying the reasoning engine, running smoke tests, and building containers.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich import print as rprint
from rich.table import Table

import agents

DEFAULT_LOCATION = (
    os.getenv("GENAI_LOCATION")
    or os.getenv("GOOGLE_GENAI_LOCATION")
    or "global"
)

console = Console()

def in_cloud_shell() -> bool:
    """Check whether the script is running inside Cloud Shell."""
    return os.getenv("CLOUD_SHELL", "").lower() == "true"


def resolve_project(explicit: Optional[str] = None) -> Optional[str]:
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

def show_menu() -> str:
    """Display an interactive menu mimicking buttons."""
    console.clear()
    rprint(Panel.fit(
        "[bold magenta]🦊 BANDIT DEPLOYMENT CENTER[/bold magenta]\n"
        "[cyan]Select an operation to execute:[/cyan]", 
        border_style="magenta"
    ))
    
    table = Table(show_header=False, box=None)
    table.add_column("Key", style="bold green")
    table.add_column("Action", style="white")
    
    table.add_row("[1]", "🚀 Deploy Reasoning Engine (Vertex AI)")
    table.add_row("[2]", "🐳 Deploy Proxy Server (Cloud Run)")
    table.add_row("[3]", "🧪 Run Smoke Test (Ping Gemini)")
    table.add_row("[4]", "📋 List Supported Models")
    table.add_row("[5]", "🛠  Update Configuration (Project/Location)")
    table.add_row("[q]", "❌ Quit")
    
    console.print(table)
    rprint("")
    
    choice = Prompt.ask("[yellow]Select an option[/yellow]", choices=["1", "2", "3", "4", "5", "q"])
    return choice

def run_reasoning_engine_deploy(project: str):
    """Trigger the deploy_reasoning_engine.py script."""
    rprint(f"\n[bold cyan]Deploying Reasoning Engine to {project}...[/bold cyan]")
    staging_bucket = Prompt.ask("Enter GCS staging bucket (e.g., gs://my-bucket)", default=f"gs://{project}-reasoning-staging")
    
    if Confirm.ask(f"Deploy using bucket {staging_bucket}?"):
        cmd = [sys.executable, "scripts/deploy_reasoning_engine.py", "--project", project, "--staging-bucket", staging_bucket]
        subprocess.run(cmd)

def run_cloud_run_deploy(project: str):
    """Trigger the Cloud Build deployment for Cloud Run."""
    rprint(f"\n[bold cyan]Deploying Proxy Server to Cloud Run...[/bold cyan]")
    if Confirm.ask("Submit build to Google Cloud Build?"):
        cmd = ["gcloud", "builds", "submit", "--config", "cloudbuild.yaml", ".", "--project", project]
        subprocess.run(cmd)

def run_smoke_test(project: str, location: str):
    """Run a prompt against the configured model."""
    rprint(f"\n[bold cyan]Running Smoke Test...[/bold cyan]")
    prompt = Prompt.ask("Enter prompt", default="Ping from LMSIFY.")
    model = Prompt.ask("Select model", default=agents.DEFAULT_MODEL)
    
    settings = agents.GenAISettings(
        model=model,
        project=project,
        location=location,
        system_instruction=None,
        api_key=os.getenv("GOOGLE_API_KEY"),
    )
    
    try:
        rprint("[dim]Sending request...[/dim]")
        response = agents.run_prompt(prompt, settings, stream=True)
        if response:
            rprint(f"\n[bold green]Response:[/bold green] {response}")
    except Exception as e:
        rprint(f"[bold red]Error:[/bold red] {e}")
        
    Prompt.ask("\nPress Enter to continue")

def list_models():
    """List supported models."""
    rprint("\n[bold cyan]Supported Models:[/bold cyan]")
    for model in agents.SUPPORTED_MODELS:
        rprint(f"  - {model}")
    Prompt.ask("\nPress Enter to continue")

def main() -> None:
    project = resolve_project()
    location = DEFAULT_LOCATION
    
    if not project:
        rprint("[bold red]Warning: No default GCP project found.[/bold red]")
        project = Prompt.ask("Please enter your Google Cloud Project ID")
    
    while True:
        choice = show_menu()
        
        if choice == '1':
            run_reasoning_engine_deploy(project)
        elif choice == '2':
            run_cloud_run_deploy(project)
        elif choice == '3':
            run_smoke_test(project, location)
        elif choice == '4':
            list_models()
        elif choice == '5':
            project = Prompt.ask("Enter new Project ID", default=project)
            location = Prompt.ask("Enter new Location", default=location)
            rprint("[green]Configuration updated![/green]")
            Prompt.ask("\nPress Enter to continue")
        elif choice == 'q':
            rprint("[magenta]Exiting Bandit Deployment Center. Goodbye![/magenta]")
            break

if __name__ == "__main__":
    main()
