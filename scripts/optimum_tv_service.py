import os
import logging
from typing import List, Dict, Optional
from optimum.optimum import API
from optimum.errors import LoginError

class OptimumTVService:
    """Service to control Optimum TV boxes via the unofficial API."""
    
    def __init__(self, optimum_id: str = None, password: str = None, device_id: str = None):
        self.optimum_id = optimum_id or os.getenv("OPTIMUM_ID")
        self.password = password or os.getenv("OPTIMUM_PASSWORD")
        self.device_id = device_id or os.getenv("OPTIMUM_DEVICE_ID")
        
        self.api = None
        if self.optimum_id and self.password and self.device_id:
            try:
                self.api = API(optimum_ID=self.optimum_id, password=self.password, device_ID=self.device_id)
                logging.info("Optimum TV API initialized successfully.")
            except LoginError as e:
                logging.error(f"Optimum Login Error: {e}")
            except Exception as e:
                logging.error(f"Optimum TV Initialization Error: {e}")
        else:
            logging.warning("Optimum credentials missing. TV control will be unavailable.")

    def list_boxes(self) -> Dict:
        """Return a list of all cable boxes."""
        if not self.api: return {}
        try:
            return {name: {"serial": box.serial, "type": box.type} for name, box in self.api.boxes.items()}
        except Exception as e:
            logging.error(f"Error listing boxes: {e}")
            return {}

    def change_channel(self, box_name: str, channel: str) -> bool:
        """Change channel by number or name (if mapped)."""
        if not self.api: return False
        box = self.api.boxes.get(box_name)
        if not box:
            logging.error(f"Box {box_name} not found.")
            return False
            
        # If channel is a name, we might need a search or mapping
        # For now, assume channel is a number string or list of keys
        keys = []
        if channel.isdigit():
            for digit in channel:
                keys.append(f"KEY_{digit}")
        else:
            # Handle special names if needed, or assume it's a key like KEY_CH_UP
            if channel.upper().startswith("KEY_"):
                keys = [channel.upper()]
            else:
                logging.warning(f"Unsupported channel format: {channel}")
                return False
                
        try:
            return self.api.do_keypress(box, keys)
        except Exception as e:
            logging.error(f"Error changing channel: {e}")
            return False

    def power_toggle(self, box_name: str) -> bool:
        """Toggle power on a specific box."""
        if not self.api: return False
        box = self.api.boxes.get(box_name)
        if not box: return False
        try:
            return self.api.do_keypress(box, ["KEY_POWER"])
        except Exception as e:
            logging.error(f"Error toggling power: {e}")
            return False

    def search_and_record(self, query: str, box_name: str) -> bool:
        """Search for content and record the first result."""
        if not self.api: return False
        box = self.api.boxes.get(box_name)
        if not box: return False
        
        try:
            results = self.api.search(query=query, max_results=1)
            if results:
                content = results[0]
                # Default settings: stop_time=0, save_days=7 (index 3), quality="HD"
                return self.api.requestSingleRecording(box, content, 0, 7, "HD")
            return False
        except Exception as e:
            logging.error(f"Error in search and record: {e}")
            return False
