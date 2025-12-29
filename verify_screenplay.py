from rich.console import Console, Group
from rich.text import Text
from rich.align import Align
from rich.panel import Panel
from rich import box
from typing import Dict, List, Optional

# Mocking ScreenplayFormatter to reproduce and fix
class ScreenplayFormatter:
    """Formats voice transcripts as movie screenplay scenes."""
    
    def __init__(self, console: Optional[Console] = None, title: str = "BANDIT VOICE SESSION"):
        self.console = console or Console()
        self.title = title
        self.scene_number = 1
        self.last_speaker = None
        
    def format_segment(self, segment: Dict, speaker: str = "USER") -> Panel:
        """Format a transcript segment as screenplay dialogue."""
        timestamp = f"{segment['start']:.1f}s - {segment['end']:.1f}s"
        scene_heading = Text(f"SCENE {self.scene_number:03d}", style="dim")
        scene_heading.append(f" [{timestamp}]", style="dim italic")
        
        # Character name
        char_style = "bold cyan" if speaker == "USER" else "bold magenta"
        char_name = Align.center(Text(speaker.upper(), style=char_style), vertical="middle")
        
        # Dialogue with confidence
        text = segment['text'].strip()
        conf = segment.get('confidence', 1.0)
        conf_mark = " [yellow]⚠[/yellow]" if conf < 0.8 else ""
        
        dialogue = Text("    " + text + conf_mark, style="white")
        
        # Parenthetical
        duration = segment['end'] - segment['start']
        parenthetical = None
        if duration < 1.0:
            parenthetical = Align.center(Text("(quickly)", style="italic dim"), vertical="middle")
        
        # --- FIXED LOGIC USING GROUP ---
        # Original broken code:
        # content = Text()
        # content.append(char_name) # Crashes here
        
        renderables = [
            scene_heading,
            Text(""), # Spacer
            char_name, 
        ]
        
        if parenthetical:
            renderables.append(parenthetical)
        
        renderables.append(dialogue)
        renderables.append(Text("")) # Spacer
        
        content = Group(*renderables)
        # -------------------------------
        
        return Panel(content, box=box.ROUNDED, border_style="dim", padding=(0, 2))

# Test
if __name__ == "__main__":
    console = Console()
    formatter = ScreenplayFormatter(console)
    seg = {"start": 0.0, "end": 2.0, "text": "Hello world", "confidence": 0.9}
    try:
        panel = formatter.format_segment(seg, "USER")
        console.print(panel)
        print("SUCCESS: Panel rendered without crash.")
    except Exception as e:
        print(f"FAIL: {e}")
