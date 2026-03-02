"""Bandit 12-Year Curriculum — Rich Colorful Test Runner 🎓

Run with beautiful emoji-rich output!
"""

import os
import sys
import time
from pathlib import Path

# Set project ID before imports
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "project-5f169828-6f8d-450b-923")

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
from rich import print as rprint
from rich.live import Live
from rich.layout import Layout

console = Console()

# 🏿 Dark skin tone emojis (priority)
EMOJI = {
    "pass": "✅",
    "fail": "❌", 
    "skip": "⏭️",
    "run": "🏃🏿",
    "wait": "⏳",
    "brain": "🧠",
    "rocket": "🚀",
    "star": "⭐",
    "fire": "🔥",
    "trophy": "🏆",
    "grad": "🎓",
    "celebrate": "🎉",
    "clap": "👏🏿",
    "muscle": "💪🏿",
    "crown": "👑",
    "diamond": "💎",
    "heart": "❤️",
    "sparkle": "✨",
    "books": "📚",
    "art": "🖼️",
    "tools": "🔧",
    "factory": "🏭",
    "robot": "🤖",
    "scroll": "📜",
    "research": "🔬",
    "write": "📝",
    "person": "🧑🏿",
    "scientist": "🧑🏿‍🔬",
    "technologist": "🧑🏿‍💻",
    "student": "🧑🏿‍🎓",
    "teacher": "🧑🏿‍🏫",
    "artist": "🧑🏿‍🎨",
}

YEAR_INFO = {
    1: {"emoji": "📚", "name": "Fundamentals", "color": "blue"},
    2: {"emoji": "🖼️", "name": "Multimodal", "color": "magenta"},
    3: {"emoji": "🔧", "name": "Tools & Reasoning", "color": "cyan"},
    4: {"emoji": "🏭", "name": "Production", "color": "green"},
    5: {"emoji": "🤖", "name": "Agent Architectures", "color": "yellow"},
    6: {"emoji": "📜", "name": "Master's Thesis", "color": "red"},
    7: {"emoji": "🎓", "name": "PhD Qualifying", "color": "blue"},
    8: {"emoji": "🎓", "name": "PhD Qualifying", "color": "blue"},
    9: {"emoji": "🔬", "name": "Dissertation Research", "color": "magenta"},
    10: {"emoji": "🔬", "name": "Dissertation Research", "color": "magenta"},
    11: {"emoji": "📝", "name": "Publication & Defense Prep", "color": "cyan"},
    12: {"emoji": "🏆", "name": "PhD Defense", "color": "green"},
}


def print_banner():
    """Print the curriculum banner"""
    banner = """
[bold magenta]╔══════════════════════════════════════════════════════════════════╗[/]
[bold magenta]║[/]     [bold white]🧑🏿‍💻 BANDIT 12-YEAR GEMINI API MASTERY CURRICULUM 🧑🏿‍🎓[/]        [bold magenta]║[/]
[bold magenta]║[/]         [italic]From Undergraduate to PhD — The Complete Journey[/]         [bold magenta]║[/]
[bold magenta]╚══════════════════════════════════════════════════════════════════╝[/]
"""
    console.print(banner)


def print_year_header(year: int, year_range: str = None):
    """Print a year header"""
    if year_range:
        info = YEAR_INFO.get(year, {"emoji": "📖", "name": "Unknown", "color": "white"})
        console.print(f"\n[bold {info['color']}]{'─'*60}[/]")
        console.print(f"[bold {info['color']}]{info['emoji']} YEARS {year_range}: {info['name'].upper()} {info['emoji']}[/]")
        console.print(f"[bold {info['color']}]{'─'*60}[/]")
    else:
        info = YEAR_INFO.get(year, {"emoji": "📖", "name": "Unknown", "color": "white"})
        console.print(f"\n[bold {info['color']}]{'─'*60}[/]")
        console.print(f"[bold {info['color']}]{info['emoji']} YEAR {year}: {info['name'].upper()} {info['emoji']}[/]")
        console.print(f"[bold {info['color']}]{'─'*60}[/]")


def run_year_tests(test_dir: str, year: int = None, year_range: str = None) -> dict:
    """Run tests for a specific year"""
    import subprocess
    
    if year:
        print_year_header(year)
    elif year_range:
        print_year_header(int(year_range.split("-")[0]), year_range)
    
    console.print(f"[dim]{EMOJI['run']} Running tests...[/]")
    
    result = subprocess.run(
        [sys.executable, "-m", "pytest", test_dir, "-v", "--tb=short", "--color=yes"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent
    )
    
    # Parse results
    output = result.stdout + result.stderr
    passed = output.count(" PASSED")
    failed = output.count(" FAILED")
    skipped = output.count(" SKIPPED")
    
    # Print summary
    if failed == 0:
        console.print(f"[bold green]{EMOJI['pass']} PASSED: {passed} | {EMOJI['skip']} Skipped: {skipped}[/]")
    else:
        console.print(f"[bold red]{EMOJI['fail']} FAILED: {failed} | {EMOJI['pass']} Passed: {passed} | {EMOJI['skip']} Skipped: {skipped}[/]")
    
    return {"passed": passed, "failed": failed, "skipped": skipped, "output": output}


def print_final_results(results: dict):
    """Print final curriculum results"""
    total_passed = sum(r["passed"] for r in results.values())
    total_failed = sum(r["failed"] for r in results.values())
    total_skipped = sum(r["skipped"] for r in results.values())
    total = total_passed + total_failed + total_skipped
    
    console.print("\n")
    
    # Results table
    table = Table(title=f"{EMOJI['trophy']} BANDIT CURRICULUM RESULTS {EMOJI['trophy']}", 
                  show_header=True, header_style="bold magenta")
    table.add_column("Year", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Passed", style="green")
    table.add_column("Failed", style="red")
    table.add_column("Skipped", style="yellow")
    
    for year_name, r in results.items():
        status = f"{EMOJI['pass']} PASS" if r["failed"] == 0 else f"{EMOJI['fail']} FAIL"
        table.add_row(year_name, status, str(r["passed"]), str(r["failed"]), str(r["skipped"]))
    
    console.print(table)
    
    # Final summary
    pass_rate = (total_passed / total * 100) if total > 0 else 0
    
    if total_failed == 0:
        console.print(Panel(
            f"""[bold green]
{EMOJI['celebrate']} {EMOJI['trophy']} CURRICULUM COMPLETE! {EMOJI['trophy']} {EMOJI['celebrate']}

{EMOJI['grad']} Bandit has achieved GEMINI API MASTERY! {EMOJI['grad']}

{EMOJI['star']} Total Tests: {total}
{EMOJI['pass']} Passed: {total_passed}
{EMOJI['skip']} Skipped: {total_skipped}
{EMOJI['fire']} Pass Rate: {pass_rate:.1f}%

{EMOJI['crown']} From Undergraduate to PhD — The Journey is Complete! {EMOJI['crown']}
{EMOJI['clap']} {EMOJI['muscle']} {EMOJI['sparkle']}
[/]""",
            title="[bold magenta]🧑🏿‍🎓 DR. BANDIT 🧑🏿‍🎓[/]",
            border_style="green"
        ))
    else:
        console.print(Panel(
            f"""[bold yellow]
{EMOJI['brain']} CURRICULUM IN PROGRESS {EMOJI['brain']}

{EMOJI['star']} Total Tests: {total}
{EMOJI['pass']} Passed: {total_passed}
{EMOJI['fail']} Failed: {total_failed}
{EMOJI['skip']} Skipped: {total_skipped}
{EMOJI['fire']} Pass Rate: {pass_rate:.1f}%

{EMOJI['muscle']} Keep learning! Failures are part of the journey!
[/]""",
            title="[bold yellow]🧑🏿‍💻 BANDIT LEARNING 🧑🏿‍💻[/]",
            border_style="yellow"
        ))


def main():
    """Run the full 12-year curriculum"""
    print_banner()
    
    console.print(f"\n[bold cyan]{EMOJI['rocket']} Starting 12-Year Gemini API Mastery Curriculum...[/]\n")
    
    results = {}
    
    # Undergraduate Years
    console.print(Panel("[bold blue]📚 UNDERGRADUATE YEARS (1-4) 📚[/]", border_style="blue"))
    
    results["Year 1"] = run_year_tests("tests/year1/", year=1)
    results["Year 2"] = run_year_tests("tests/year2/", year=2)
    results["Year 3"] = run_year_tests("tests/year3/", year=3)
    results["Year 4"] = run_year_tests("tests/year4/", year=4)
    
    # Master's Years
    console.print(Panel("[bold magenta]📜 MASTER'S YEARS (5-6) 📜[/]", border_style="magenta"))
    
    results["Year 5"] = run_year_tests("tests/year5/", year=5)
    results["Year 6"] = run_year_tests("tests/year6/", year=6)
    
    # PhD Years
    console.print(Panel("[bold green]🎓 PhD YEARS (7-12) 🎓[/]", border_style="green"))
    
    results["Years 7-8"] = run_year_tests("tests/year7_8/", year_range="7-8")
    results["Years 9-10"] = run_year_tests("tests/year9_10/", year_range="9-10")
    results["Year 11"] = run_year_tests("tests/year11/", year=11)
    results["Year 12"] = run_year_tests("tests/year12/", year=12)
    
    # Final results
    print_final_results(results)


if __name__ == "__main__":
    main()
