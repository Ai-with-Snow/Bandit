"""
BANDIT HARNESS - INITIALIZER AGENT
Sets up the persistent context artifacts for the long-running agent loop.
"""
import os
import json
import datetime

HARNESS_DIR = os.path.join(os.path.dirname(__file__))
FEATURE_LIST_PATH = os.path.join(HARNESS_DIR, "feature_list.json")
PROGRESS_PATH = os.path.join(HARNESS_DIR, "bandit_progress.json")

def initialize_harness():
    print("🤖 BANDIT INITIALIZER AGENT")
    print("===========================")
    
    # 1. Ensure Directory Exists
    os.makedirs(HARNESS_DIR, exist_ok=True)
    
    # 2. Check/Create Feature List
    if not os.path.exists(FEATURE_LIST_PATH):
        print("Creating feature_list.json...")
        # (Content would be the full curriculum mapping, keeping it minimal here for safety)
        # In a real scenario, this would generate the full 200 item list from the PRD
        features = {
            "features": [
                {"id": "Y1_FUNDAMENTALS", "status": "passed", "desc": "Year 1 Mastery"},
                {"id": "Y2_MULTIMODAL", "status": "pending", "desc": "Year 2 Multimodal"}
            ]
        }
        with open(FEATURE_LIST_PATH, 'w') as f:
            json.dump(features, f, indent=2)
    else:
        print(f"✅ feature_list.json exists.")

    # 3. Check/Create Progress Log
    if not os.path.exists(PROGRESS_PATH):
        print("Creating bandit_progress.json...")
        progress = {
            "sessions": [],
            "current_state": "Initialized"
        }
        with open(PROGRESS_PATH, 'w') as f:
            json.dump(progress, f, indent=2)
    else:
        print(f"✅ bandit_progress.json exists.")
        
    print("\nInitialization Complete. Ready for Coding Agent.")

if __name__ == "__main__":
    initialize_harness()
