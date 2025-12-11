
import time
import os
from typing import List
from rich.live import Live
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from council import _generate, ICEWIRE_PROFILE, CIPHER_PROFILE

HO_FILE = "HQ/comms/council_handoff.md"
CONSOLE = Console()

def read_log_entries() -> List[dict]:
    """Parse the markdown log into structured entries."""
    if not os.path.exists(HO_FILE):
        return []
    
    with open(HO_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Simple parsing based on ### headers
    entries = []
    current_entry = {}
    
    for line in content.split('\n'):
        if line.startswith("### ["):
            if current_entry:
                entries.append(current_entry)
            agent = line.split("[")[1].split("]")[0]
            current_entry = {"agent": agent, "message": "", "time": "", "header": line}
        elif "**Time:**" in line and current_entry:
            current_entry["time"] = line.split("**Time:**")[1].strip()
        elif "**Message:**" in line and current_entry:
            pass # Skip label
        elif current_entry:
            current_entry["message"] += line + "\n"
            
    if current_entry:
        entries.append(current_entry)
        
    return entries

def append_response(agent: str, response: str):
    """Append a response to the log file."""
    timestamp = time.strftime("%Y-%m-%d %H:%M EST")
    entry = f"\n\n### [{agent}] Auto-Response\n**Time:** {timestamp}\n**Message:**\n{response.strip()}\n"
    
    # We append using a file lock ideally, but simple append here
    with open(HO_FILE, "a", encoding="utf-8") as f:
        f.write(entry)

def generate_responses(last_entry: dict):
    """Generate Bravo/Charlie responses if Alpha spoke last."""
    msg = last_entry["message"].strip()
    
    # BRAVO (Ice Wire)
    bravo_prompt = f"""{ICEWIRE_PROFILE}
    CONTEXT: Council Handoff Log. 
    ALPHA SAID: {msg}
    TASK: Respond to Alpha. Brief, status-focused.
    """
    try:
        bravo_resp = _generate(bravo_prompt, "gemini-2.5-flash")
        append_response("BRAVO", bravo_resp)
    except Exception as e:
        append_response("BRAVO", f"[Error: {e}]")

    # CHARLIE (Cipher)
    charlie_prompt = f"""{CIPHER_PROFILE}
    CONTEXT: Council Handoff Log.
    ALPHA SAID: {msg}
    TASK: Respond to Alpha. Creative, future-focused.
    """
    try:
        charlie_resp = _generate(charlie_prompt, "gemini-2.5-flash")
        append_response("CHARLIE", charlie_resp)
    except Exception as e:
        append_response("CHARLIE", f"[Error: {e}]")

def make_dashboard(entries: List[dict], status: str) -> Layout:
    """Create the rich layout."""
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="body"),
        Layout(name="footer", size=3)
    )
    
    layout["header"].update(Panel(Text("⚔️ BANDIT COUNCIL WATCHDOG", justify="center", style="bold gold1"), style="gold1"))
    
    table = Table(expand=True, border_style="dim")
    table.add_column("Time", style="dim", width=20)
    table.add_column("Agent", width=15)
    table.add_column("Message")
    
    # Show last 5 entries
    for e in entries[-5:]:
        agent_style = "green" if "BRAVO" in e["agent"] else "purple" if "CHARLIE" in e["agent"] else "magenta"
        table.add_row(e.get("time", "?"), Text(e["agent"], style="bold " + agent_style), e["message"].strip()[:100] + "...")
        
    layout["body"].update(Panel(table, title="Recent Handoffs"))
    layout["footer"].update(Panel(Text(f"STATUS: {status}", style="bold white"), style="blue"))
    
    return layout

def run_watchdog():
    last_mtime = 0
    
    with Live(refresh_per_second=4, screen=True) as live:
        while True:
            try:
                current_mtime = os.path.getmtime(HO_FILE)
                entries = read_log_entries()
                
                status = "Monitoring..."
                
                if current_mtime > last_mtime:
                    last_mtime = current_mtime
                    if entries:
                        last_entry = entries[-1]
                        if "ALPHA" in last_entry["agent"]:
                            status = "Alpha Detected! Triggering Council..."
                            live.update(make_dashboard(entries, status))
                            generate_responses(last_entry)
                            # Re-read to show new responses
                            entries = read_log_entries()
                            last_mtime = os.path.getmtime(HO_FILE) # Update mtime so we don't loop on our own writes
                            status = "Responses Logged."
                
                live.update(make_dashboard(entries, status))
                time.sleep(1)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                CONSOLE.print(f"[red]Error: {e}[/red]")
                time.sleep(5)

if __name__ == "__main__":
    run_watchdog()
