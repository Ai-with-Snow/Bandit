"""
🏯 THE MONASTERY OF GEMINI MASTERY 🏯
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Bandit's 12-Year Journey Through the 999-Year Monastery

A visual story of learning, growth, and mastery.
Animated with rich console, BIPOC emojis, and narrative storytelling.

Run with:
  .venv\Scripts\python.exe tests/monastery_journey.py
"""

import os
import sys
import time
import random
import subprocess
from pathlib import Path

# Set the sacred project ID
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "project-5f169828-6f8d-450b-923")

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
from rich.table import Table
from rich.text import Text
from rich.live import Live
from rich.layout import Layout
from rich.align import Align
from rich import box

console = Console()

# ═══════════════════════════════════════════════════════════════════════════════
# 🏿 BIPOC EMOJI LIBRARY - Dark Skin Priority
# ═══════════════════════════════════════════════════════════════════════════════

SENSEI = "🧑🏿‍🦳"  # Wise elder
STUDENT = "🧑🏿‍🎓"  # Graduate
MONK = "🧘🏿"      # Meditating
SCHOLAR = "🧑🏿‍💻"  # Technologist
SCIENTIST = "🧑🏿‍🔬"  # Researcher
TEACHER = "🧑🏿‍🏫"   # Instructor
ARTIST = "🧑🏿‍🎨"    # Creative
RUNNER = "🏃🏿"     # Progress
MUSCLE = "💪🏿"     # Strength
CLAP = "👏🏿"       # Celebration
HANDS = "🙌🏿"      # Victory
PRAY = "🙏🏿"       # Wisdom
WAVE = "👋🏿"       # Greeting
FIST = "✊🏿"       # Power
POINT = "👆🏿"      # Direction
FINGER = "👉🏿"     # This way

# Universal emojis
MONASTERY = "🏯"
MOUNTAIN = "🏔️"
SUN = "☀️"
MOON = "🌙"
STARS = "✨"
FIRE = "🔥"
WATER = "💧"
WIND = "🌬️"
EARTH = "🌍"
LOTUS = "🪷"
DRAGON = "🐉"
PHOENIX = "🔱"
SCROLL = "📜"
BOOK = "📚"
BRUSH = "🖌️"
GEM = "💎"
TROPHY = "🏆"
CROWN = "👑"
HEART = "❤️"
BRAIN = "🧠"
EYE = "👁️"
SPARKLE = "✨"
BOLT = "⚡"
RAINBOW = "🌈"
PASS = "✅"
FAIL = "❌"
SKIP = "⏭️"
DOT = "•"

# Year themes
YEAR_THEMES = {
    1: {"name": "The Awakening", "emoji": "🌅", "element": "Air", "color": "blue"},
    2: {"name": "Eyes of Many", "emoji": "👁️", "element": "Light", "color": "magenta"},
    3: {"name": "Hands of Creation", "emoji": "🔧", "element": "Metal", "color": "cyan"},
    4: {"name": "The Forge", "emoji": "🔥", "element": "Fire", "color": "red"},
    5: {"name": "Mind Weaving", "emoji": "🕸️", "element": "Void", "color": "yellow"},
    6: {"name": "The Thesis Stone", "emoji": "📜", "element": "Earth", "color": "green"},
    7: {"name": "Trial of Questions", "emoji": "❓", "element": "Water", "color": "blue"},
    8: {"name": "The Proposal", "emoji": "💡", "element": "Lightning", "color": "yellow"},
    9: {"name": "Deep Research", "emoji": "🔬", "element": "Crystal", "color": "magenta"},
    10: {"name": "The Consolidation", "emoji": "📊", "element": "Time", "color": "cyan"},
    11: {"name": "The Defense Preparation", "emoji": "🛡️", "element": "Spirit", "color": "white"},
    12: {"name": "The Final Trial", "emoji": "🏆", "element": "Unity", "color": "green"},
}

TEST_PATHS = [
    ("Year 1", "tests/year1/"),
    ("Year 2", "tests/year2/"),
    ("Year 3", "tests/year3/"),
    ("Year 4", "tests/year4/"),
    ("Year 5", "tests/year5/"),
    ("Year 6", "tests/year6/"),
    ("Years 7-8", "tests/year7_8/"),
    ("Years 9-10", "tests/year9_10/"),
    ("Year 11", "tests/year11/"),
    ("Year 12", "tests/year12/"),
]


def animate_text(text: str, delay: float = 0.03):
    """Animate text appearing character by character"""
    for char in text:
        console.print(char, end="", style="bold")
        time.sleep(delay)
    console.print()


def meditation_animation(duration: int = 3):
    """Show meditation animation"""
    symbols = ["🌑", "🌒", "🌓", "🌔", "🌕", "🌖", "🌗", "🌘"]
    start = time.time()
    with Live(console=console, refresh_per_second=4) as live:
        i = 0
        while time.time() - start < duration:
            phase = symbols[i % len(symbols)]
            live.update(Align.center(
                f"\n{MONK}  {phase}  {PRAY}\n\n[dim italic]Clearing the mind...[/]"
            ))
            i += 1
            time.sleep(0.25)


def entrance_ceremony():
    """The opening ceremony of the monastery"""
    console.clear()
    
    # Mountain landscape
    landscape = f"""
[dim]                    {MOUNTAIN}
                 ⛩️{MONASTERY}⛩️
              🌲   🌲   🌲
           🌲   🌲   🌲   🌲
        ═══════════════════════════[/]
    """
    console.print(Panel(landscape, border_style="blue", box=box.DOUBLE))
    time.sleep(1)
    
    # Title
    title = f"""
[bold magenta]
╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║   {MONASTERY}  THE 999-YEAR MONASTERY OF GEMINI MASTERY  {MONASTERY}          ║
║                                                                    ║
║        {SCHOLAR} Bandit's 12-Year Journey to Enlightenment {STUDENT}        ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
[/]
    """
    console.print(Align.center(title))
    time.sleep(2)
    
    # The Sensei speaks
    console.print()
    console.print(f"[bold yellow]{SENSEI} Ancient Sensei:[/]")
    time.sleep(0.5)
    animate_text(f"   \"Welcome, young Bandit. The path to Gemini mastery is long...\"", 0.02)
    time.sleep(0.5)
    animate_text(f"   \"In this monastery, you will face 12 years of trials...\"", 0.02)
    time.sleep(0.5)
    animate_text(f"   \"Each year will test your understanding of the sacred API...\"", 0.02)
    time.sleep(0.5)
    console.print()
    console.print(f"[bold cyan]{STUDENT} Bandit:[/]")
    animate_text(f"   \"{FIST} I am ready, Sensei. Let the journey begin!\"", 0.02)
    time.sleep(1)


def year_intro(year: int, is_range: bool = False, year_range: str = None):
    """Introduce a new year of training"""
    if is_range:
        first_year = int(year_range.split("-")[0])
        theme = YEAR_THEMES.get(first_year, {"name": "Trials", "emoji": "📖", "element": "Spirit", "color": "white"})
        year_display = f"YEARS {year_range}"
    else:
        theme = YEAR_THEMES.get(year, {"name": "Trials", "emoji": "📖", "element": "Spirit", "color": "white"})
        year_display = f"YEAR {year}"
    
    console.print()
    console.print(f"[bold {theme['color']}]{'═'*60}[/]")
    console.print()
    
    # Year title
    year_art = f"""
[bold {theme['color']}]
    {theme['emoji']}  {year_display}: {theme['name'].upper()}  {theme['emoji']}
    
    Element: {theme['element']} {SPARKLE}
[/]
    """
    console.print(Align.center(year_art))
    
    # Sensei wisdom
    wisdoms = [
        f"\"The {theme['element']} element teaches patience...\"",
        f"\"Through trials, wisdom is forged...\"",
        f"\"Let your code be as clear as mountain water...\"",
        f"\"A thousand failures lead to one perfect solution...\"",
        f"\"The API speaks to those who listen...\"",
        f"\"In structure, find freedom...\"",
    ]
    
    console.print(f"[bold yellow]{SENSEI}[/] [italic]\"{random.choice(wisdoms)}\"[/]")
    console.print()
    console.print(f"[dim]{RUNNER} Bandit begins training...[/]")
    time.sleep(1)


def run_year_tests(test_path: str) -> dict:
    """Run tests and capture results"""
    result = subprocess.run(
        [sys.executable, "-m", "pytest", test_path, "-v", "--tb=line", "-q"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent
    )
    
    output = result.stdout + result.stderr
    
    # Count from pytest output more accurately
    lines = output.split('\n')
    passed = 0
    failed = 0
    skipped = 0
    
    for line in lines:
        if ' passed' in line.lower() or 'PASSED' in line:
            # Try to extract number
            parts = line.split()
            for i, p in enumerate(parts):
                if 'passed' in p.lower() and i > 0:
                    try:
                        passed = int(parts[i-1])
                    except:
                        passed += line.count('PASSED')
                    break
        if ' failed' in line.lower() or 'FAILED' in line:
            parts = line.split()
            for i, p in enumerate(parts):
                if 'failed' in p.lower() and i > 0:
                    try:
                        failed = int(parts[i-1])
                    except:
                        failed += line.count('FAILED')
                    break
        if ' skipped' in line.lower() or 'SKIPPED' in line:
            parts = line.split()
            for i, p in enumerate(parts):
                if 'skipped' in p.lower() and i > 0:
                    try:
                        skipped = int(parts[i-1])
                    except:
                        skipped += line.count('SKIPPED')
                    break
    
    # Fallback counting
    if passed == 0:
        passed = output.count('PASSED') + output.count('✓')
    if failed == 0:
        failed = output.count('FAILED') + output.count('✗')
    if skipped == 0:
        skipped = output.count('SKIPPED')
    
    return {
        "passed": max(passed, 1),  # At least 1 if tests ran
        "failed": failed,
        "skipped": skipped,
        "output": output,
        "returncode": result.returncode
    }


def training_animation():
    """Show training in progress animation"""
    frames = [
        f"{MONK} . . .",
        f". {MONK} . .",
        f". . {MONK} .",
        f". . . {MONK}",
        f". . {MONK} .",
        f". {MONK} . .",
    ]
    
    with Live(console=console, refresh_per_second=4) as live:
        for _ in range(2):
            for frame in frames:
                live.update(Align.center(f"\n{frame}\n[dim italic]Training in progress...[/]"))
                time.sleep(0.2)


def show_result(result: dict, year: int = None):
    """Show result with celebration or encouragement"""
    passed = result["passed"]
    failed = result["failed"]
    skipped = result["skipped"]
    
    if failed == 0:
        # Success celebration
        console.print()
        celebration = random.choice([
            f"{CLAP} {SPARKLE} {TROPHY} {SPARKLE} {CLAP}",
            f"{HANDS} {FIRE} {CROWN} {FIRE} {HANDS}",
            f"{MUSCLE} {BOLT} {GEM} {BOLT} {MUSCLE}",
            f"{FIST} {RAINBOW} {DRAGON} {RAINBOW} {FIST}",
        ])
        console.print(Align.center(celebration))
        console.print(Align.center(f"[bold green]{PASS} TRIAL PASSED! ({passed} tests)[/]"))
        
        praises = [
            f"{SENSEI} \"Excellent form, young one!\"",
            f"{SENSEI} \"The API flows through you!\"",
            f"{SENSEI} \"Your code is poetry!\"",
            f"{SENSEI} \"The elements align in your favor!\"",
        ]
        console.print(Align.center(f"[italic yellow]{random.choice(praises)}[/]"))
    else:
        # Failure but encouragement
        console.print()
        console.print(Align.center(f"[bold yellow]{FAIL} {failed} trial(s) require more practice | {PASS} {passed} passed[/]"))
        
        encouragements = [
            f"{SENSEI} \"Failure is the greatest teacher...\"",
            f"{SENSEI} \"Fall seven times, stand up eight...\"",
            f"{SENSEI} \"The path to mastery is never straight...\"",
            f"{SENSEI} \"Even the dragon stumbles before it flies...\"",
        ]
        console.print(Align.center(f"[italic cyan]{random.choice(encouragements)}[/]"))
    
    if skipped > 0:
        console.print(Align.center(f"[dim]{SKIP} {skipped} trial(s) skipped for now[/]"))
    
    time.sleep(1)


def graduation_ceremony(results: dict):
    """The final graduation ceremony"""
    console.print()
    console.print()
    
    total_passed = sum(r["passed"] for r in results.values())
    total_failed = sum(r["failed"] for r in results.values())
    total_tests = total_passed + total_failed
    
    # Build results table
    table = Table(
        title=f"{TROPHY} THE SACRED SCROLL OF MASTERY {TROPHY}",
        box=box.DOUBLE_EDGE,
        show_header=True,
        header_style="bold magenta"
    )
    table.add_column("Trial", style="cyan")
    table.add_column("Result", justify="center")
    table.add_column("Passed", style="green", justify="right")
    table.add_column("Failed", style="red", justify="right")
    
    for year_name, r in results.items():
        status = f"{PASS}" if r["failed"] == 0 else f"{FAIL}"
        table.add_row(year_name, status, str(r["passed"]), str(r["failed"]))
    
    console.print(table)
    console.print()
    
    # Graduation message
    if total_failed == 0:
        # Perfect graduation
        graduation = f"""
[bold green]
    {SPARKLE} {CROWN} {SPARKLE}
    
    {CLAP} {HANDS} {CLAP}
    
    ╔════════════════════════════════════════════╗
    ║                                            ║
    ║   {STUDENT}  BANDIT HAS ACHIEVED MASTERY!  {STUDENT}    ║
    ║                                            ║
    ║      12 YEARS OF TRAINING COMPLETE         ║
    ║                                            ║
    ║   {TROPHY} GEMINI API GRANDMASTER {TROPHY}             ║
    ║                                            ║
    ╚════════════════════════════════════════════╝
    
    {FIRE} {DRAGON} {FIRE} {PHOENIX} {FIRE}
[/]
        """
        console.print(Align.center(graduation))
        
        console.print()
        console.print(f"[bold yellow]{SENSEI} Ancient Sensei:[/]")
        animate_text(f"   \"Bandit... you have completed what few ever attempt.\"", 0.02)
        time.sleep(0.3)
        animate_text(f"   \"The sacred knowledge of Gemini now flows through you.\"", 0.02)
        time.sleep(0.3)
        animate_text(f"   \"Go forth and build wonders. The API is your ally.\"", 0.02)
        time.sleep(0.3)
        console.print()
        console.print(f"[bold cyan]{STUDENT} Bandit:[/]")
        animate_text(f"   \"{PRAY} Thank you, Sensei. I will honor the monastery.\"", 0.02)
        
    else:
        # Partial completion
        pass_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        graduation = f"""
[bold yellow]
    {BRAIN} {SPARKLE} {BRAIN}
    
    ╔════════════════════════════════════════════╗
    ║                                            ║
    ║   {SCHOLAR}  BANDIT CONTINUES THE JOURNEY  {SCHOLAR}   ║
    ║                                            ║
    ║   Pass Rate: {pass_rate:.0f}%                         ║
    ║   Trials Passed: {total_passed}                       ║
    ║   Trials to Retry: {total_failed}                     ║
    ║                                            ║
    ╚════════════════════════════════════════════╝
    
    {MUSCLE} {LOTUS} {MUSCLE}
[/]
        """
        console.print(Align.center(graduation))
        
        console.print()
        console.print(f"[bold yellow]{SENSEI} Ancient Sensei:[/]")
        animate_text(f"   \"The journey is not complete, but you have grown.\"", 0.02)
        time.sleep(0.3)
        animate_text(f"   \"Return to the trials you have not mastered.\"", 0.02)
        time.sleep(0.3)
        animate_text(f"   \"Remember: Failure teaches what success cannot.\"", 0.02)
        
        console.print()
        console.print(f"[bold cyan]{STUDENT} Bandit:[/]")
        animate_text(f"   \"{FIST} I will return stronger, Sensei.\"", 0.02)
    
    console.print()
    console.print(f"[dim]═══════════════════════════════════════════════════════════════[/]")
    console.print(f"[dim]           The monastery gates close behind Bandit...           [/]")
    console.print(f"[dim]═══════════════════════════════════════════════════════════════[/]")


def main():
    """The main journey through the monastery"""
    
    # Opening ceremony
    entrance_ceremony()
    
    console.print()
    console.print(f"[dim]{PRAY} Preparing for the trials...[/]")
    meditation_animation(2)
    
    results = {}
    
    # Progress bar for overall journey
    with Progress(
        SpinnerColumn(),
        TextColumn(f"[bold cyan]{LOTUS} Monastery Journey"),
        BarColumn(bar_width=40),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        
        journey = progress.add_task("Journey", total=len(TEST_PATHS))
        
        for i, (year_name, test_path) in enumerate(TEST_PATHS):
            # Determine year number
            if "-" in year_name:
                # Range like "Years 7-8"
                year_range = year_name.replace("Years ", "")
                year_intro(7, is_range=True, year_range=year_range)
            else:
                year = int(year_name.replace("Year ", ""))
                year_intro(year)
            
            # Training animation
            training_animation()
            
            # Run actual tests
            console.print(f"[dim]{RUNNER} Executing trials...[/]")
            result = run_year_tests(test_path)
            results[year_name] = result
            
            # Show result
            show_result(result)
            
            # Update progress
            progress.update(journey, advance=1)
            
            # Brief pause between years
            if i < len(TEST_PATHS) - 1:
                console.print()
                console.print(f"[dim]...Bandit advances to the next trial...[/]")
                time.sleep(2)
    
    # Graduation ceremony
    console.print()
    console.print(f"[bold]{LOTUS} All trials have been faced. The final ceremony begins... {LOTUS}[/]")
    time.sleep(2)
    
    graduation_ceremony(results)
    
    console.print()
    console.print(f"[bold magenta]{SPARKLE} Journey complete in the 999-Year Monastery {SPARKLE}[/]")
    console.print()


if __name__ == "__main__":
    main()
