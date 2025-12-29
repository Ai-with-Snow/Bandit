#!/usr/bin/env python3
"""Sync HQ folder to GCS bucket."""
import os
import subprocess
import sys

def main():
    # Get the HQ directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    hq_dir = os.path.join(script_dir, "HQ")
    bucket = "gs://bandit-hq-docs/HQ"
    
    print(f"Syncing {hq_dir} to {bucket}...")
    
    # Try using gcloud storage command
    try:
        result = subprocess.run(
            ["gcloud", "storage", "rsync", hq_dir, bucket, "--recursive"],
            capture_output=True,
            text=True,
            timeout=300
        )
        if result.returncode == 0:
            print("✅ Sync complete!")
            print(result.stdout)
        else:
            print(f"Error: {result.stderr}")
            # Fallback to gsutil
            print("Trying gsutil...")
            result2 = subprocess.run(
                ["gsutil", "-m", "rsync", "-r", hq_dir, bucket],
                capture_output=True,
                text=True,
                timeout=300
            )
            if result2.returncode == 0:
                print("✅ Sync complete via gsutil!")
            else:
                print(f"gsutil error: {result2.stderr}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
