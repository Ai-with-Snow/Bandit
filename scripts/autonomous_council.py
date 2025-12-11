import time
import os
import sys
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.console import Console
from rich.text import Text
from rich.markdown import Markdown

# Ensure we can import from the same directory
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from council import _generate, BANDIT_PROFILE, ICEWIRE_PROFILE, CIPHER_PROFILE

# Configuration
LOG_FILE = os.path.abspath("HQ/comms/council_handoff.md")
CYCLE_DELAY = 10  # Seconds between turns

console = Console()

class CouncilState:
    def __init__(self):
        self.alpha_last = ""
        self.bravo_last = ""
        self.charlie_last = ""
        self.status = "Initializing..."
        self.last_update = datetime.now()

state = CouncilState()

def read_log():
    """Reads the log file and updates state."""
    try:
        with open(LOG_FILE, "r", encoding='utf-8') as f:
            content = f.read()
            
        # Naive parsing - mostly for display updates
        # In a real app we'd want more robust parsing
        if "### [ALPHA]" in content:
            state.alpha_last = content.split("### [ALPHA]")[-1].split("###")[0].strip()
        if "### [BRAVO]" in content:
            state.bravo_last = content.split("### [BRAVO]")[-1].split("###")[0].strip()
        if "### [CHARLIE]" in content:
            state.charlie_last = content.split("### [CHARLIE]")[-1].split("###")[0].strip()
            
    except Exception as e:
        state.status = f"Error reading log: {e}"

def make_layout() -> Layout:
    """Define the grid layout."""
    layout = Layout(name="root")
    layout.split(
        Layout(name="header", size=3),
        Layout(name="main", ratio=1),
        Layout(name="footer", size=3)
    )
    
    layout["main"].split_row(
        Layout(name="bravo", ratio=1),
        Layout(name="alpha", ratio=2),
        Layout(name="charlie", ratio=1),
    )
    return layout

def update_display(layout: Layout):
    """Update the content of the layout."""
    
    # Header
    layout["header"].update(
        Panel(
            Text(f"COUNCIL LIVE FEED | Active Agents: ALPHA, BRAVO, CHARLIE", justify="center", style="bold white"),
            style="bold blue"
        )
    )
    
    # Alpha (Bandit)
    layout["alpha"].update(
        Panel(
            Markdown(state.alpha_last[-1000:] if state.alpha_last else "Waiting for Alpha..."),
            title="[bold magenta]ALPHA (Bandit)[/bold magenta]",
            border_style="magenta"
        )
    )
    
    # Bravo (Ice Wire)
    layout["bravo"].update(
        Panel(
            Markdown(state.bravo_last[-800:] if state.bravo_last else "Waiting for Bravo..."),
            title="[bold green]BRAVO (Ice Wire)[/bold green]",
            border_style="green"
        )
    )
    
    # Charlie (Cipher)
    layout["charlie"].update(
        Panel(
            Markdown(state.charlie_last[-800:] if state.charlie_last else "Waiting for Charlie..."),
            title="[bold purple]CHARLIE (Cipher)[/bold purple]",
            border_style="purple"
        )
    )
    
    # Footer (Status)
    layout["footer"].update(
        Panel(
            Text(f"STATUS: {state.status} | Last Update: {state.last_update.strftime('%H:%M:%S')}", style="dim"),
            border_style="dim"
        )
    )

class LogHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if os.path.abspath(event.src_path) == LOG_FILE:
            read_log()
            state.last_update = datetime.now()

def run_agent_cycle():
    """Checks who needs to speak and generates content."""
    
    with open(LOG_FILE, "r", encoding='utf-8') as f:
        content = f.read()

    # Determine whose turn it is based on the LAST entry
    # Order: Alpha -> Bravo -> Charlie -> Alpha...
    
    last_header_idx = -1
    last_agent = None
    
    agents = ["ALPHA", "BRAVO", "CHARLIE"]
    
    for agent in agents:
        idx = content.lower().rfind(f"### [{agent.lower()}]")
        # Fallback for mixed case or different bracket styles if needed, 
        # but our script writes strictly `### [AGENT]`
        if idx == -1:
             idx = content.rfind(f"### [{agent}]")
             
        if idx > last_header_idx:
            last_header_idx = idx
            last_agent = agent
            
    # Default to Alpha if empty or unknown
    if last_agent is None:
        next_agent = "ALPHA"
    elif last_agent == "ALPHA":
        next_agent = "BRAVO"
    elif last_agent == "BRAVO":
        next_agent = "CHARLIE"
    elif last_agent == "CHARLIE":
        next_agent = "ALPHA"
    else:
        next_agent = "ALPHA"

    state.status = f"Processing turn: {next_agent}"
    
    # Extract context (last message)
    if last_agent:
        context_msg = content[last_header_idx:].strip()
    else:
        context_msg = "Initial startup. Council is convening."

    # Generate Response
    response = ""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M EST")
    
    if next_agent == "ALPHA":
        prompt = f"""{BANDIT_PROFILE}
        CONTEXT: You are reading the Council Log.
        PREVIOUS UPDATE: {context_msg}
        
        TASK: Synthesize the input from Bravo/Charlie (if any) and issue a new directive or status update.
        Keep it brief (max 3 sentences). Status: [SYSTEM OK / DIRECTIVE ISSUED].
        """
        response = _generate(prompt, "gemini-2.5-pro")
        
    elif next_agent == "BRAVO":
        prompt = f"""{ICEWIRE_PROFILE}
        CONTEXT: You are reading the Council Log.
        ALPHA'S MESSAGE: {context_msg}
        
        TASK: Acknowledge Alpha. Provide infrastructure/signal status.
        Keep it brief (max 3 sentences). Data-focused.
        """
        response = _generate(prompt, "gemini-2.5-flash")
        
    elif next_agent == "CHARLIE":
        prompt = f"""{CIPHER_PROFILE}
        CONTEXT: You are reading the Council Log.
        PREVIOUS UPDATE: {context_msg}
        
        TASK: Provide a security scan or creative insight based on the thread.
        Keep it brief (max 3 sentences). Abstract/Pattern-focused.
        """
        response = _generate(prompt, "gemini-2.5-flash")
    
    # Write to log
    entry = f"\n\n### [{next_agent}] Update\n**Time:** {timestamp}\n**Message:**\n{response.strip()}\n"
    
    with open(LOG_FILE, "a", encoding='utf-8') as f:
        f.write(entry)
        
    state.status = f"Posted update for {next_agent}. Waiting..."
    read_log() # Force update local state

def main():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", encoding='utf-8') as f:
            f.write("# Council Handoff Log\n\nStarting autonomous cycle...\n")

    # Initial read
    read_log()

    # Setup Watchdog
    event_handler = LogHandler()
    observer = Observer()
    # Watch the directory, not just the file, to be safe with some editors doing atomic moves
    observer.schedule(event_handler, path=os.path.dirname(LOG_FILE), recursive=False)
    observer.start()

    # Rich Layout
    layout = make_layout()

    last_cycle_time = 0
    
    try:
        with Live(layout, refresh_per_second=4, screen=True) as live:
            while True:
                current_time = time.time()
                
                # Check if it's time for an agent to act
                if current_time - last_cycle_time > CYCLE_DELAY:
                    # Run logic in a way that doesn't block UI too much 
                    # (in a real app, use threading, here we accept a small freeze during API call)
                    state.status = "Thinking..."
                    update_display(layout)
                    live.refresh()
                    
                    try:
                        run_agent_cycle()
                    except Exception as e:
                        state.status = f"Error in cycle: {e}"
                    
                    last_cycle_time = time.time()
                
                update_display(layout)
                time.sleep(0.1)
                
    except KeyboardInterrupt:
        observer.stop()
        console.print("[yellow]Council adjourned.[/yellow]")
    
    observer.join()

if __name__ == "__main__":
    main()
