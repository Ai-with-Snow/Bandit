"""File watcher for HQ directory - automatically syncs on changes.

This script monitors the HQ directory for changes and triggers automatic sync to GCS.
Useful for development when frequently updating knowledge base documents.

Requirements: pip install watchdog
"""

import time
import subprocess
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

HQ_DIRECTORY = "HQ"
SYNC_SCRIPT = "scripts/sync_hq_to_gcs.py"
DEBOUNCE_SECONDS = 5  # Wait 5 seconds after last change before syncing

class HQChangeHandler(FileSystemEventHandler):
    """Handler for HQ directory changes."""
    
    def __init__(self):
        self.last_modified = time.time()
        self.pending_sync = False
    
    def on_modified(self, event):
        """Triggered when a file is modified."""
        if event.is_directory:
            return
        
        # Only sync markdown files
        if not event.src_path.endswith('.md'):
            return
        
        print(f"📝 Detected change: {event.src_path}")
        self.last_modified = time.time()
        self.pending_sync = True
    
    def on_created(self, event):
        """Triggered when a new file is created."""
        if event.is_directory:
            return
        
        if not event.src_path.endswith('.md'):
            return
        
        print(f"✨ New file created: {event.src_path}")
        self.last_modified = time.time()
        self.pending_sync = True
    
    def on_deleted(self, event):
        """Triggered when a file is deleted."""
        if event.is_directory:
            return
        
        print(f"🗑️  File deleted: {event.src_path}")
        self.last_modified = time.time()
        self.pending_sync = True
    
    def check_and_sync(self):
        """Check if enough time has passed and trigger sync if needed."""
        if not self.pending_sync:
            return
        
        # Wait for debounce period
        if time.time() - self.last_modified < DEBOUNCE_SECONDS:
            return
        
        print(f"\n🔄 Triggering sync after {DEBOUNCE_SECONDS}s of inactivity...")
        try:
            result = subprocess.run(
                ["py", "-3.12", SYNC_SCRIPT],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(result.stdout)
                print("✅ Sync completed successfully\n")
            else:
                print(f"❌ Sync failed: {result.stderr}\n")
        
        except Exception as e:
            print(f"❌ Error running sync: {e}\n")
        
        self.pending_sync = False

def main():
    """Start watching HQ directory for changes."""
    hq_path = Path(HQ_DIRECTORY)
    
    if not hq_path.exists():
        print(f"❌ Error: {HQ_DIRECTORY} directory not found!")
        return
    
    print("=" * 60)
    print("  HQ Directory Watcher")
    print("=" * 60)
    print(f"\n👁️  Watching: {hq_path.absolute()}")
    print(f"⏱️  Debounce: {DEBOUNCE_SECONDS} seconds")
    print("\nPress Ctrl+C to stop...\n")
    
    event_handler = HQChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, str(hq_path), recursive=True)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
            event_handler.check_and_sync()
    except KeyboardInterrupt:
        print("\n\n⏹️  Stopping watcher...")
        observer.stop()
    
    observer.join()
    print("✅ Watcher stopped")

if __name__ == "__main__":
    try:
        main()
    except ModuleNotFoundError:
        print("❌ Error: 'watchdog' package not installed")
        print("\nInstall it with:")
        print("  pip install watchdog")
        print("\nOr add to requirements.txt and run:")
        print("  pip install -r requirements.txt")
