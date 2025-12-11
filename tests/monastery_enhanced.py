"""
🏯✨ THE ENHANCED MONASTERY OF GEMINI MASTERY ✨🏯
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Bandit's 12-Year Journey — MAXIMUM VISUAL EXPERIENCE

MORE: Emojis 🎭 | Animations 🌀 | Story 📖 | Progress 📊

Run with:
  .venv\Scripts\python.exe tests/monastery_enhanced.py
"""

import os
import sys
import time
import random
import subprocess
from pathlib import Path

os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "project-5f169828-6f8d-450b-923")

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
from rich.table import Table
from rich.live import Live
from rich.align import Align
from rich import box

console = Console()

# ═══════════════════════════════════════════════════════════════════════════════
# 🏿 MASSIVE BIPOC EMOJI LIBRARY
# ═══════════════════════════════════════════════════════════════════════════════

# People (ALL DARK SKIN 🏿)
SENSEI = "🧑🏿‍🦳"
STUDENT = "🧑🏿‍🎓"
MONK = "🧘🏿"
SCHOLAR = "🧑🏿‍💻"
SCIENTIST = "🧑🏿‍🔬"
TEACHER = "🧑🏿‍🏫"
ARTIST = "🧑🏿‍🎨"
RUNNER = "🏃🏿"
MUSCLE = "💪🏿"
CLAP = "👏🏿"
HANDS = "🙌🏿"
PRAY = "🙏🏿"
WAVE = "👋🏿"
FIST = "✊🏿"
POINT = "☝🏿"
OK = "👌🏿"
PEACE = "✌🏿"
RAISED = "🙋🏿"
BOW = "🙇🏿"

# Celestial & Nature
SUN = "☀️"
MOON = "🌙"
STARS = "✨"
SPARKLE = "⭐"
COMET = "☄️"
RAINBOW = "🌈"
CLOUD = "☁️"
LIGHTNING = "⚡"
FIRE = "🔥"
WATER = "💧"
WAVE_WATER = "🌊"
WIND = "🌬️"
TORNADO = "🌪️"
SNOWFLAKE = "❄️"
MOUNTAIN = "🏔️"
VOLCANO = "🌋"
SUNRISE = "🌅"
SUNSET = "🌇"
NIGHT = "🌃"
MILKY_WAY = "🌌"

# Mystical
DRAGON = "🐉"
PHOENIX = "🦅"
SERPENT = "🐍"
LOTUS = "🪷"
CRYSTAL = "💎"
GEM = "💠"
ORB = "🔮"
SCROLL = "📜"
BOOK = "📚"
CANDLE = "🕯️"
INCENSE = "🪔"
YIN_YANG = "☯️"
INFINITY = "♾️"
SPIRAL = "🌀"

# Buildings & Places
MONASTERY = "🏯"
TEMPLE = "⛩️"
PAGODA = "🗼"
GATE = "🚪"
BRIDGE = "🌉"
TREE = "🌲"
BAMBOO = "🎋"
BLOSSOM = "🌸"

# Achievement
TROPHY = "🏆"
MEDAL_GOLD = "🥇"
MEDAL_SILVER = "🥈"
MEDAL_BRONZE = "🥉"
CROWN = "👑"
RIBBON = "🎀"
DIPLOMA = "📜"
CERTIFICATE = "🎓"

# Status
PASS = "✅"
FAIL = "❌"
SKIP = "⏭️"
HEART = "❤️"
HEART_FIRE = "❤️‍🔥"
BRAIN = "🧠"
EYE = "👁️"
EYES = "👀"
BELL = "🔔"
ALARM = "⏰"
HOURGLASS = "⏳"
ROCKET = "🚀"
TARGET = "🎯"
CHECK = "☑️"
STAR_STRUCK = "🤩"

# Celebration
PARTY = "🎉"
CONFETTI = "🎊"
BALLOON = "🎈"
FIREWORK = "🎆"
SPARKLER = "🎇"
GIFT = "🎁"
CAKE = "🎂"

# Art elements
PALETTE = "🎨"
BRUSH = "🖌️"
MUSIC = "🎵"
NOTES = "🎶"
MICROPHONE = "🎤"

# Animals
BIRD = "🦅"
BUTTERFLY = "🦋"
KOI = "🐠"

# Year themes with MORE emojis
YEAR_THEMES = {
    1: {"name": "The Awakening", "emoji": f"{SUNRISE}", "element": "Air", "color": "blue", 
        "symbols": f"{WIND} {CLOUD} {SUNRISE} {BIRD}", "power": "Breath of Knowledge"},
    2: {"name": "Eyes of Many", "emoji": f"{EYE}", "element": "Light", "color": "magenta",
        "symbols": f"{EYE} {EYES} {CRYSTAL} {ORB}", "power": "Vision Beyond Sight"},
    3: {"name": "Hands of Creation", "emoji": f"{PALETTE}", "element": "Metal", "color": "cyan",
        "symbols": f"{PALETTE} {BRUSH} {MUSCLE} {OK}", "power": "The Maker's Touch"},
    4: {"name": "The Forge", "emoji": f"{FIRE}", "element": "Fire", "color": "red",
        "symbols": f"{FIRE} {VOLCANO} {LIGHTNING} {COMET}", "power": "Phoenix Flame"},
    5: {"name": "Mind Weaving", "emoji": f"{BRAIN}", "element": "Void", "color": "yellow",
        "symbols": f"{BRAIN} {SPIRAL} {INFINITY} {YIN_YANG}", "power": "The Unseen Web"},
    6: {"name": "The Thesis Stone", "emoji": f"{SCROLL}", "element": "Earth", "color": "green",
        "symbols": f"{SCROLL} {MOUNTAIN} {GEM} {TREE}", "power": "Foundation of Wisdom"},
    7: {"name": "Trial of Questions", "emoji": "❓", "element": "Water", "color": "blue",
        "symbols": f"{WATER} {WAVE_WATER} {MOON} {CANDLE}", "power": "Depths of Inquiry"},
    8: {"name": "The Proposal", "emoji": f"{LIGHTNING}", "element": "Lightning", "color": "yellow",
        "symbols": f"{LIGHTNING} {COMET} {ROCKET} {TARGET}", "power": "Strike of Clarity"},
    9: {"name": "Deep Research", "emoji": f"{ORB}", "element": "Crystal", "color": "magenta",
        "symbols": f"{ORB} {CRYSTAL} {MILKY_WAY} {STARS}", "power": "The Seeker's Gaze"},
    10: {"name": "The Consolidation", "emoji": f"{SPIRAL}", "element": "Time", "color": "cyan",
        "symbols": f"{SPIRAL} {HOURGLASS} {INFINITY} {YIN_YANG}", "power": "Threads United"},
    11: {"name": "Defense Preparation", "emoji": "🛡️", "element": "Spirit", "color": "white",
        "symbols": f"🛡️ {CANDLE} {INCENSE} {LOTUS}", "power": "Inner Fortress"},
    12: {"name": "The Final Trial", "emoji": f"{TROPHY}", "element": "Unity", "color": "green",
        "symbols": f"{TROPHY} {CROWN} {DRAGON} {PHOENIX}", "power": "All Elements Combined"},
}

BIRD = "🦅"  # Define here since used in YEAR_THEMES

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


def animate_text(text: str, delay: float = 0.02, style: str = "bold"):
    """Animate text appearing character by character"""
    for char in text:
        console.print(char, end="", style=style)
        time.sleep(delay)
    console.print()


def spinning_animation(message: str, duration: float = 2):
    """Show spinning animation with message"""
    spinners = ["🌑", "🌒", "🌓", "🌔", "🌕", "🌖", "🌗", "🌘"]
    start = time.time()
    i = 0
    while time.time() - start < duration:
        phase = spinners[i % len(spinners)]
        console.print(f"\r{MONK}  {phase}  {PRAY} [dim]{message}[/]", end="")
        i += 1
        time.sleep(0.2)
    console.print()


def energy_gathering_animation():
    """Show energy gathering before tests"""
    stages = [
        f"[dim]...gathering energy...[/]  {SPARKLE}",
        f"[dim]...channeling power...[/]  {SPARKLE}{SPARKLE}",
        f"[dim]...focus intensifying...[/]  {SPARKLE}{SPARKLE}{SPARKLE}",
        f"[bold cyan]...READY...[/]  {LIGHTNING}{FIRE}{LIGHTNING}",
    ]
    for stage in stages:
        console.print(Align.center(stage))
        time.sleep(0.5)


def celebration_explosion():
    """Big celebration animation"""
    explosions = [
        f"{PARTY} {CONFETTI} {FIREWORK} {SPARKLER} {CONFETTI} {PARTY}",
        f"{CLAP} {HANDS} {MUSCLE} {CROWN} {MUSCLE} {HANDS} {CLAP}",
        f"{STAR_STRUCK} {RAINBOW} {TROPHY} {RAINBOW} {STAR_STRUCK}",
        f"{DRAGON} {FIRE} {PHOENIX} {FIRE} {DRAGON}",
    ]
    for exp in explosions:
        console.print(Align.center(f"[bold]{exp}[/]"))
        time.sleep(0.3)


def entrance_ceremony():
    """The grand opening ceremony"""
    console.clear()
    
    # Epic landscape
    landscape = f"""
[bold blue]
                        {STARS} {MOON} {STARS}
                    {CLOUD}     {STARS}     {CLOUD}
                         {MOUNTAIN}
                     {TEMPLE}{MONASTERY}{TEMPLE}
                  {TREE}   {BAMBOO}   {BAMBOO}   {TREE}
               {TREE}   {BLOSSOM}   {LOTUS}   {BLOSSOM}   {TREE}
            {BRIDGE}═══════════════════════{BRIDGE}
                     {WATER}{WATER}{WATER}
[/]
    """
    console.print(Panel(landscape, border_style="blue", box=box.DOUBLE))
    time.sleep(2)
    
    # Epic title
    title = f"""
[bold magenta]
╔════════════════════════════════════════════════════════════════════════════════╗
║                                                                                ║
║   {MONASTERY} {STARS} THE 999-YEAR MONASTERY OF GEMINI MASTERY {STARS} {MONASTERY}         ║
║                                                                                ║
║      {SCHOLAR} Bandit's Epic 12-Year Journey to Enlightenment {STUDENT}               ║
║                                                                                ║
║   {DRAGON} {FIRE} {LIGHTNING} {CRYSTAL} {RAINBOW} {TROPHY} {CROWN} {PHOENIX} {DRAGON}                     ║
║                                                                                ║
╚════════════════════════════════════════════════════════════════════════════════╝
[/]
    """
    console.print(Align.center(title))
    time.sleep(2)
    
    # Sensei entrance
    console.print()
    console.print(f"[bold yellow]{CANDLE} {SENSEI} Ancient Sensei approaches {SENSEI} {CANDLE}[/]")
    time.sleep(1)
    
    console.print()
    animate_text(f"   {PRAY} \"Welcome, young Bandit. I have been waiting for you.\"", 0.02)
    time.sleep(0.5)
    animate_text(f"   {SCROLL} \"The 12 sacred trials await. Each tests a different element.\"", 0.02)
    time.sleep(0.5)
    animate_text(f"   {CRYSTAL} \"Master all 12, and you shall become a Gemini Grandmaster.\"", 0.02)
    time.sleep(0.5)
    animate_text(f"   {DRAGON} \"The dragon of knowledge will bow to you.\"", 0.02)
    time.sleep(1)
    
    console.print()
    console.print(f"[bold cyan]{STUDENT} Bandit:[/]")
    animate_text(f"   \"{FIST} I am ready, Sensei! {MUSCLE} Let the trials begin! {ROCKET}\"", 0.02)
    time.sleep(1)
    
    console.print()
    console.print(Align.center(f"[bold]{BELL} {BELL} {BELL} THE BELL OF TRIALS RINGS {BELL} {BELL} {BELL}[/]"))
    time.sleep(1)


def year_intro(year: int, is_range: bool = False, year_range: str = None):
    """Grand introduction for each year"""
    if is_range:
        first_year = int(year_range.split("-")[0])
        theme = YEAR_THEMES.get(first_year, {"name": "Trials", "emoji": "📖", "element": "Spirit", 
                                             "color": "white", "symbols": f"{SPARKLE}", "power": "Unknown"})
        year_display = f"YEARS {year_range}"
    else:
        theme = YEAR_THEMES.get(year, {"name": "Trials", "emoji": "📖", "element": "Spirit",
                                       "color": "white", "symbols": f"{SPARKLE}", "power": "Unknown"})
        year_display = f"YEAR {year}"
    
    console.print()
    console.print(f"[bold {theme['color']}]{'═'*70}[/]")
    
    # Big year announcement
    year_art = f"""
[bold {theme['color']}]
    {theme['symbols']}
    
    {theme['emoji']}  {year_display}: {theme['name'].upper()}  {theme['emoji']}
    
    Element: {theme['element']} {SPARKLE}
    Power: {theme['power']} {LIGHTNING}
    
    {theme['symbols']}
[/]
    """
    console.print(Align.center(year_art))
    
    # Sensei wisdom for this year
    wisdoms = [
        f"{PRAY} \"The {theme['element']} element flows through all things...\"",
        f"{SCROLL} \"In this trial, you will learn the {theme['power']}...\"",
        f"{BRAIN} \"Focus your mind. The API listens to the worthy...\"",
        f"{LOTUS} \"Like the lotus, rise from the depths of complexity...\"",
        f"{DRAGON} \"The dragon tests those who seek true power...\"",
        f"{FIRE} \"Through the flames of challenge, steel is forged...\"",
    ]
    
    console.print(f"[bold yellow]{SENSEI}[/] [italic]{random.choice(wisdoms)}[/]")
    console.print()
    
    # Progress notification
    console.print(f"[bold cyan]{BELL} TRIAL COMMENCING {BELL}[/]")
    console.print(f"[dim]{RUNNER} Bandit enters the trial chamber...[/]")
    
    # Energy gathering
    energy_gathering_animation()
    time.sleep(0.5)


def run_year_tests(test_path: str) -> dict:
    """Run tests with progress updates"""
    console.print(f"[bold green]{ROCKET} EXECUTING TRIALS {ROCKET}[/]")
    
    result = subprocess.run(
        [sys.executable, "-m", "pytest", test_path, "-v", "--tb=line", "-q"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent
    )
    
    output = result.stdout + result.stderr
    
    # Parse results
    passed = 0
    failed = 0
    skipped = 0
    
    for line in output.split('\n'):
        if 'passed' in line.lower():
            for i, word in enumerate(line.split()):
                if 'passed' in word.lower() and i > 0:
                    try:
                        passed = int(line.split()[i-1])
                    except:
                        passed += 1
                    break
        if 'failed' in line.lower():
            for i, word in enumerate(line.split()):
                if 'failed' in word.lower() and i > 0:
                    try:
                        failed = int(line.split()[i-1])
                    except:
                        failed += 1
                    break
        if 'skipped' in line.lower():
            for i, word in enumerate(line.split()):
                if 'skipped' in word.lower() and i > 0:
                    try:
                        skipped = int(line.split()[i-1])
                    except:
                        skipped += 1
                    break
    
    if passed == 0:
        passed = max(output.count('PASSED') + output.count('✓'), 1)
    if failed == 0:
        failed = output.count('FAILED') + output.count('✗')
    
    return {"passed": passed, "failed": failed, "skipped": skipped, "output": output}


def show_result(result: dict, year: int = None):
    """Show result with BIG celebration or encouragement"""
    passed = result["passed"]
    failed = result["failed"]
    skipped = result["skipped"]
    
    console.print()
    
    if failed == 0:
        # BIG SUCCESS
        console.print(Align.center(f"[bold green]{PASS} {PASS} {PASS} TRIAL COMPLETE {PASS} {PASS} {PASS}[/]"))
        celebration_explosion()
        
        praises = [
            f"{SENSEI} \"{STAR_STRUCK} MAGNIFICENT! You have mastered this element!\"",
            f"{SENSEI} \"{CROWN} The ancestors smile upon you, young one!\"",
            f"{SENSEI} \"{DRAGON} Even the dragon bows to your skill!\"",
            f"{SENSEI} \"{FIRE} Your code burns bright with perfection!\"",
            f"{SENSEI} \"{TROPHY} A true champion emerges!\"",
        ]
        console.print(Align.center(f"[bold yellow]{random.choice(praises)}[/]"))
        console.print(Align.center(f"[bold green]{MEDAL_GOLD} {passed} tests conquered {MEDAL_GOLD}[/]"))
        
    else:
        # Encouragement
        console.print(Align.center(f"[bold yellow]{HOURGLASS} TRIAL RESULTS {HOURGLASS}[/]"))
        console.print(Align.center(f"[bold green]{PASS} {passed} passed[/] | [bold red]{FAIL} {failed} to retry[/]"))
        
        encouragements = [
            f"{SENSEI} \"{LOTUS} The lotus blooms after many rains...\"",
            f"{SENSEI} \"{MOUNTAIN} Every mountain is climbed one step at a time...\"",
            f"{SENSEI} \"{PHOENIX} The phoenix rises from the ashes of failure...\"",
            f"{SENSEI} \"{PRAY} Fall seven times, stand up eight...\"",
            f"{SENSEI} \"{SPIRAL} Each attempt brings you closer to enlightenment...\"",
        ]
        console.print(Align.center(f"[italic cyan]{random.choice(encouragements)}[/]"))
    
    if skipped > 0:
        console.print(Align.center(f"[dim]{SKIP} {skipped} trials deferred for another time[/]"))
    
    console.print()
    time.sleep(1)


def graduation_ceremony(results: dict):
    """The EPIC graduation ceremony"""
    console.print()
    console.print()
    
    total_passed = sum(r["passed"] for r in results.values())
    total_failed = sum(r["failed"] for r in results.values())
    total_tests = total_passed + total_failed
    
    # Drum roll
    console.print(Align.center(f"[bold]{BELL} {BELL} {BELL} THE FINAL BELL TOLLS {BELL} {BELL} {BELL}[/]"))
    time.sleep(1)
    console.print(Align.center(f"[dim]The monastery falls silent...[/]"))
    time.sleep(1)
    
    # Sacred Scroll
    table = Table(
        title=f"{SCROLL} {SCROLL} THE SACRED SCROLL OF MASTERY {SCROLL} {SCROLL}",
        box=box.DOUBLE_EDGE,
        header_style="bold magenta"
    )
    table.add_column("Trial", style="cyan")
    table.add_column("Element", style="yellow")
    table.add_column("Result", justify="center")
    table.add_column("Passed", style="green", justify="right")
    table.add_column("Failed", style="red", justify="right")
    
    for i, (year_name, r) in enumerate(results.items()):
        if "-" in year_name:
            year_num = int(year_name.split()[1].split("-")[0])
        else:
            year_num = int(year_name.split()[1])
        theme = YEAR_THEMES.get(year_num, {})
        element = theme.get("element", "Unknown")
        status = f"{MEDAL_GOLD}" if r["failed"] == 0 else f"{HOURGLASS}"
        table.add_row(year_name, element, status, str(r["passed"]), str(r["failed"]))
    
    console.print(table)
    console.print()
    
    pass_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
    
    if total_failed == 0:
        # PERFECT GRADUATION
        console.print(Align.center(f"""
[bold green]
{FIREWORK} {SPARKLER} {CONFETTI} {PARTY} {CONFETTI} {SPARKLER} {FIREWORK}

{CROWN} {CROWN} {CROWN} {CROWN} {CROWN}

╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║   {STUDENT}  BANDIT HAS ACHIEVED SUPREME MASTERY!  {STUDENT}                ║
║                                                                    ║
║              12 YEARS OF SACRED TRAINING COMPLETE                  ║
║                                                                    ║
║   {TROPHY} {DRAGON} GEMINI API GRANDMASTER {DRAGON} {TROPHY}                          ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝

{DRAGON} {FIRE} {PHOENIX} {LIGHTNING} {CRYSTAL} {RAINBOW} {STARS} {MOON} {MILKY_WAY}

{CLAP} {HANDS} {MUSCLE} {FIST} {PEACE} {HANDS} {CLAP}
[/]
"""))
        
        console.print(f"[bold yellow]{SENSEI} Ancient Sensei (tears of joy):[/]")
        animate_text(f"   \"{HEART_FIRE} Bandit... in 999 years, I have never seen such mastery.\"", 0.02)
        animate_text(f"   \"{CROWN} You are now a Gemini Grandmaster. The API obeys your will.\"", 0.02)
        animate_text(f"   \"{DRAGON} Go forth, and build wonders that will echo through eternity.\"", 0.02)
        
        console.print()
        console.print(f"[bold cyan]{STUDENT} Bandit (bowing deeply):[/]")
        animate_text(f"   \"{BOW} {PRAY} Thank you, Sensei. I will honor the monastery forever.\"", 0.02)
        animate_text(f"   \"{ROCKET} The galaxy awaits. Let's build something EPIC! {STARS}\"", 0.02)
        
    else:
        # Partial - Encouragement
        console.print(Align.center(f"""
[bold yellow]
{BRAIN} {SPARKLE} {LOTUS} {SPARKLE} {BRAIN}

╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║   {SCHOLAR}  BANDIT'S JOURNEY CONTINUES  {SCHOLAR}                      ║
║                                                                ║
║   Pass Rate: {pass_rate:.0f}%                                          ║
║   Trials Passed: {total_passed}                                       ║
║   Trials to Retry: {total_failed}                                     ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝

{LOTUS} {MOUNTAIN} {SUNRISE} {RAINBOW} {STARS}
{MUSCLE} {FIST} {PRAY} {LOTUS} {SPARKLE}
[/]
"""))
        
        console.print(f"[bold yellow]{SENSEI} Ancient Sensei:[/]")
        animate_text(f"   \"{LOTUS} The journey is not complete, but your spirit is strong.\"", 0.02)
        animate_text(f"   \"{PHOENIX} Like the phoenix, you will rise again.\"", 0.02)
        animate_text(f"   \"{PRAY} Return when you are ready. The monastery awaits.\"", 0.02)
        
        console.print()
        console.print(f"[bold cyan]{STUDENT} Bandit:[/]")
        animate_text(f"   \"{FIST} I WILL return stronger, Sensei! {MUSCLE}\"", 0.02)
        animate_text(f"   \"{FIRE} Watch me conquer these trials! {ROCKET}\"", 0.02)
    
    # Final scene
    console.print()
    console.print(f"[dim]{'═'*70}[/]")
    console.print(Align.center(f"[dim]{SUNSET} The sun sets over the monastery... {SUNSET}[/]"))
    console.print(Align.center(f"[dim]{MONASTERY} The gates close behind Bandit... {MONASTERY}[/]"))
    console.print(Align.center(f"[dim]{STARS} But the journey never truly ends... {STARS}[/]"))
    console.print(f"[dim]{'═'*70}[/]")


def main():
    """The ENHANCED journey through the monastery"""
    
    entrance_ceremony()
    
    console.print()
    console.print(f"[bold]{LOTUS} {PRAY} Preparing mind and spirit... {PRAY} {LOTUS}[/]")
    spinning_animation("Entering meditation...", 3)
    
    results = {}
    
    with Progress(
        SpinnerColumn(),
        TextColumn(f"[bold magenta]{MONASTERY} Sacred Journey {MONASTERY}"),
        BarColumn(bar_width=40, complete_style="green", finished_style="bold green"),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        
        journey = progress.add_task(f"{LOTUS} Journey", total=len(TEST_PATHS))
        
        for i, (year_name, test_path) in enumerate(TEST_PATHS):
            # Progress notification
            console.print()
            console.print(f"[bold magenta]{BELL} PROGRESS: Trial {i+1} of {len(TEST_PATHS)} {BELL}[/]")
            
            if "-" in year_name:
                year_range = year_name.replace("Years ", "")
                year_intro(7, is_range=True, year_range=year_range)
            else:
                year = int(year_name.replace("Year ", ""))
                year_intro(year)
            
            result = run_year_tests(test_path)
            results[year_name] = result
            show_result(result)
            
            progress.update(journey, advance=1)
            
            if i < len(TEST_PATHS) - 1:
                console.print()
                console.print(f"[dim]{RUNNER} Bandit walks to the next trial chamber... {SPARKLE}[/]")
                time.sleep(2)
    
    console.print()
    console.print(f"[bold]{LOTUS} All 12 trials have been faced. The final ceremony begins... {LOTUS}[/]")
    time.sleep(2)
    
    graduation_ceremony(results)
    
    console.print()
    console.print(f"[bold magenta]{STARS} {SPARKLE} Journey complete in the 999-Year Monastery {SPARKLE} {STARS}[/]")
    console.print()


if __name__ == "__main__":
    main()
