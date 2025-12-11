"""Bandit Curriculum - Rich Live Output with 🏿 Emojis

Real-time test progress with dark skin tone priority emojis and progress bars.
"""

import os
import sys
import time

# Set project ID
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "project-5f169828-6f8d-450b-923")

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint

console = Console()

# 🏿 Dark skin tone emojis ALWAYS
EMOJI = {
    "pass": "✅",
    "fail": "❌", 
    "skip": "⏭️",
    "run": "🏃🏿",
    "brain": "🧠",
    "rocket": "🚀",
    "trophy": "🏆",
    "grad": "🎓",
    "celebrate": "🎉",
    "clap": "👏🏿",
    "muscle": "💪🏿",
    "crown": "👑",
    "sparkle": "✨",
    "person": "🧑🏿",
    "scientist": "🧑🏿‍🔬",
    "technologist": "🧑🏿‍💻",
    "student": "🧑🏿‍🎓",
}

YEARS = [
    ("Year 1", "tests/year1/", "📚 Fundamentals", "blue"),
    ("Year 2", "tests/year2/", "🖼️ Multimodal", "magenta"),
    ("Year 3", "tests/year3/", "🔧 Tools & Reasoning", "cyan"),
    ("Year 4", "tests/year4/", "🏭 Production", "green"),
    ("Year 5", "tests/year5/", "🤖 Agent Architectures", "yellow"),
    ("Year 6", "tests/year6/", "📜 Master's Thesis", "red"),
    ("Years 7-8", "tests/year7_8/", "🎓 PhD Qualifying", "blue"),
    ("Years 9-10", "tests/year9_10/", "🔬 Dissertation", "magenta"),
    ("Year 11", "tests/year11/", "📝 Defense Prep", "cyan"),
    ("Year 12", "tests/year12/", "🏆 PhD Defense", "green"),
]


def run_tests_live(test_path: str) -> dict:
    """Run tests and capture output with live updates"""
    import subprocess
    
    result = subprocess.run(
        [sys.executable, "-m", "pytest", test_path, "-v", "--tb=line", "-q"],
        capture_output=True,
        text=True,
        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    
    output = result.stdout + result.stderr
    passed = output.count(" PASSED") + output.count(" passed")
    failed = output.count(" FAILED") + output.count(" failed")
    skipped = output.count(" SKIPPED") + output.count(" skipped")
    
    return {
        "passed": passed or output.count("✓"),
        "failed": failed or output.count("✗"),
        "skipped": skipped,
        "returncode": result.returncode,
        "output": output
    }


def main():
    console.print(Panel(
        f"[bold magenta]{EMOJI['technologist']} BANDIT 12-YEAR GEMINI API MASTERY {EMOJI['student']}[/]\n"
        f"[italic]From Undergraduate to PhD — Live Progress[/]",
        border_style="magenta"
    ))
    
    console.print(f"\n{EMOJI['rocket']} [bold cyan]Starting curriculum tests...[/]\n")
    time.sleep(2)
    
    results = {}
    total_passed = 0
    total_failed = 0
    total_skipped = 0
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(bar_width=30),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        console=console,
        transient=False
    ) as progress:
        
        curriculum_task = progress.add_task(
            f"{EMOJI['brain']} Running 12-Year Curriculum...",
            total=len(YEARS)
        )
        
        for year_name, test_path, description, color in YEARS:
            # Show current year
            console.print(f"\n[bold {color}]{'─'*50}[/]")
            console.print(f"[bold {color}]{description} - {year_name}[/]")
            console.print(f"[bold {color}]{'─'*50}[/]")
            console.print(f"{EMOJI['run']} [dim]Running tests...[/]")
            
            # Run tests
            result = run_tests_live(test_path)
            results[year_name] = result
            
            passed = result["passed"]
            failed = result["failed"]
            skipped = result["skipped"]
            
            total_passed += passed
            total_failed += failed
            total_skipped += skipped
            
            # Show result
            if failed == 0:
                console.print(f"{EMOJI['pass']} [bold green]PASSED: {passed}[/] | {EMOJI['skip']} Skipped: {skipped}")
            else:
                console.print(f"{EMOJI['fail']} [bold red]FAILED: {failed}[/] | {EMOJI['pass']} Passed: {passed} | {EMOJI['skip']} Skipped: {skipped}")
            
            progress.update(curriculum_task, advance=1)
    
    # Final results
    console.print("\n")
    
    table = Table(
        title=f"{EMOJI['trophy']} CURRICULUM RESULTS {EMOJI['trophy']}",
        show_header=True,
        header_style="bold magenta"
    )
    table.add_column("Year", style="cyan")
    table.add_column("Status", justify="center")
    table.add_column("Passed", style="green", justify="right")
    table.add_column("Failed", style="red", justify="right")
    
    for year_name, result in results.items():
        status = f"{EMOJI['pass']}" if result["failed"] == 0 else f"{EMOJI['fail']}"
        table.add_row(
            year_name,
            status,
            str(result["passed"]),
            str(result["failed"])
        )
    
    console.print(table)
    
    # Final summary
    total = total_passed + total_failed + total_skipped
    pass_rate = (total_passed / total * 100) if total > 0 else 0
    
    if total_failed == 0:
        console.print(Panel(
            f"""[bold green]
{EMOJI['celebrate']} {EMOJI['trophy']} CURRICULUM COMPLETE! {EMOJI['trophy']} {EMOJI['celebrate']}

{EMOJI['grad']} Bandit achieved GEMINI API MASTERY! {EMOJI['grad']}

{EMOJI['pass']} Passed: {total_passed}/{total}
{EMOJI['sparkle']} Pass Rate: {pass_rate:.0f}%

{EMOJI['crown']} DR. BANDIT {EMOJI['crown']}
{EMOJI['clap']} {EMOJI['muscle']} {EMOJI['sparkle']}
[/]""",
            title=f"[bold magenta]{EMOJI['student']} GRADUATION {EMOJI['student']}[/]",
            border_style="green"
        ))
    else:
        console.print(Panel(
            f"""[bold yellow]
{EMOJI['brain']} LEARNING IN PROGRESS {EMOJI['brain']}

{EMOJI['pass']} Passed: {total_passed}
{EMOJI['fail']} Failed: {total_failed}
{EMOJI['skip']} Skipped: {total_skipped}
Pass Rate: {pass_rate:.0f}%

{EMOJI['muscle']} Failures are part of learning!
[/]""",
            title=f"[bold yellow]{EMOJI['technologist']} BANDIT TRAINING {EMOJI['technologist']}[/]",
            border_style="yellow"
        ))


if __name__ == "__main__":
    main()
