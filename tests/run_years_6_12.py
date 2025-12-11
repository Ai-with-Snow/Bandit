"""Run Years 6-12 Only — Rich Live Output with 🏿 Emojis"""

import os
import sys
import time

os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "project-5f169828-6f8d-450b-923")

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
from rich.panel import Panel
from rich.table import Table

console = Console()

EMOJI = {
    "pass": "✅", "fail": "❌", "run": "🏃🏿", "brain": "🧠", "trophy": "🏆",
    "grad": "🎓", "celebrate": "🎉", "clap": "👏🏿", "muscle": "💪🏿",
    "sparkle": "✨", "technologist": "🧑🏿‍💻", "student": "🧑🏿‍🎓",
}

YEARS = [
    ("Year 6", "tests/year6/", "📜 Master's Thesis", "red"),
    ("Years 7-8", "tests/year7_8/", "🎓 PhD Qualifying", "blue"),
    ("Years 9-10", "tests/year9_10/", "🔬 Dissertation", "magenta"),
    ("Year 11", "tests/year11/", "📝 Defense Prep", "cyan"),
    ("Year 12", "tests/year12/", "🏆 PhD Defense", "green"),
]


def run_tests(test_path: str) -> dict:
    import subprocess
    result = subprocess.run(
        [sys.executable, "-m", "pytest", test_path, "-v", "--tb=line", "-q"],
        capture_output=True, text=True,
        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    output = result.stdout + result.stderr
    passed = output.count(" PASSED") + output.count(" passed") + output.count("✓")
    failed = output.count(" FAILED") + output.count(" failed") + output.count("✗")
    skipped = output.count(" SKIPPED") + output.count(" skipped")
    return {"passed": passed, "failed": failed, "skipped": skipped, "output": output}


def main():
    console.print(Panel(
        f"[bold magenta]{EMOJI['technologist']} YEARS 6-12: Master's + PhD {EMOJI['student']}[/]\n"
        f"[italic]Project ID FIXED — Let's go![/]",
        border_style="magenta"
    ))
    
    time.sleep(2)
    results = {}
    
    with Progress(SpinnerColumn(), TextColumn("[bold blue]{task.description}"),
                  BarColumn(bar_width=30), TaskProgressColumn(), TimeElapsedColumn(),
                  console=console) as progress:
        
        task = progress.add_task(f"{EMOJI['brain']} Running Years 6-12...", total=len(YEARS))
        
        for year_name, test_path, description, color in YEARS:
            console.print(f"\n[bold {color}]{'─'*50}[/]")
            console.print(f"[bold {color}]{description} - {year_name}[/]")
            console.print(f"{EMOJI['run']} [dim]Running tests...[/]")
            
            result = run_tests(test_path)
            results[year_name] = result
            
            if result["failed"] == 0:
                console.print(f"{EMOJI['pass']} [bold green]PASSED: {result['passed']}[/]")
            else:
                console.print(f"{EMOJI['fail']} [bold red]FAILED: {result['failed']}[/] | {EMOJI['pass']} Passed: {result['passed']}")
            
            progress.update(task, advance=1)
    
    # Results table
    table = Table(title=f"{EMOJI['trophy']} YEARS 6-12 RESULTS {EMOJI['trophy']}")
    table.add_column("Year", style="cyan")
    table.add_column("Status", justify="center")
    table.add_column("Passed", style="green", justify="right")
    table.add_column("Failed", style="red", justify="right")
    
    total_passed = sum(r["passed"] for r in results.values())
    total_failed = sum(r["failed"] for r in results.values())
    
    for year_name, r in results.items():
        status = f"{EMOJI['pass']}" if r["failed"] == 0 else f"{EMOJI['fail']}"
        table.add_row(year_name, status, str(r["passed"]), str(r["failed"]))
    
    console.print("\n")
    console.print(table)
    
    if total_failed == 0:
        console.print(Panel(f"[bold green]{EMOJI['celebrate']} ALL YEARS 6-12 PASSED! {EMOJI['celebrate']}[/]", border_style="green"))
    else:
        console.print(Panel(f"[bold yellow]{EMOJI['muscle']} Passed: {total_passed} | Failed: {total_failed}[/]", border_style="yellow"))


if __name__ == "__main__":
    main()
