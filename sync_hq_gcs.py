#!/usr/bin/env python3
"""Sync HQ folder to GCS bucket using Python API."""
import os
import sys
from pathlib import Path

try:
    from google.cloud import storage
except ImportError:
    print("Installing google-cloud-storage...")
    os.system("pip3 install --user --break-system-packages google-cloud-storage")
    from google.cloud import storage

BUCKET_NAME = "bandit-hq-docs"
HQ_PREFIX = "HQ"

def sync_folder_to_gcs(local_folder: str, bucket_name: str, prefix: str):
    """Upload all files from local folder to GCS bucket."""
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    
    local_path = Path(local_folder)
    uploaded = 0
    skipped = 0
    
    for file_path in local_path.rglob("*"):
        if file_path.is_file():
            # Create blob name relative to HQ folder
            relative_path = file_path.relative_to(local_path)
            blob_name = f"{prefix}/{relative_path}".replace("\\", "/")
            
            blob = bucket.blob(blob_name)
            
            # Check if file needs updating (by comparing sizes)
            try:
                blob.reload()
                if blob.size == file_path.stat().st_size:
                    skipped += 1
                    continue
            except:
                pass  # Blob doesn't exist, upload it
            
            print(f"Uploading: {blob_name}")
            blob.upload_from_filename(str(file_path))
            uploaded += 1
    
    print(f"\n✅ Sync complete!")
    print(f"   Uploaded: {uploaded} files")
    print(f"   Skipped (unchanged): {skipped} files")

if __name__ == "__main__":
    # Get HQ folder path
    script_dir = Path(__file__).parent.resolve()
    hq_folder = script_dir / "HQ"
    
    if not hq_folder.exists():
        print(f"Error: HQ folder not found at {hq_folder}")
        sys.exit(1)
    
    print(f"🔄 Syncing {hq_folder} to gs://{BUCKET_NAME}/{HQ_PREFIX}")
    print("-" * 50)
    
    try:
        sync_folder_to_gcs(str(hq_folder), BUCKET_NAME, HQ_PREFIX)
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure you're authenticated with: gcloud auth application-default login")
        sys.exit(1)
