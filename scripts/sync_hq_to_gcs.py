"""Automated sync of HQ directory to Google Cloud Storage.

This script syncs the local HQ directory to the GCS bucket used by Vertex AI Search.
Run manually or as a scheduled task to keep the knowledge base up to date.
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from google.cloud import storage
from google.cloud import discoveryengine_v1 as discoveryengine

# Configuration
PROJECT_ID = "project-5f169828-6f8d-450b-923"
BUCKET_NAME = "bandit-hq-knowledge-bucket"
DATA_STORE_ID = "bandit-hq-knowledge_1765072850414"
DATA_STORE_LOCATION = "global"
HQ_DIRECTORY = "HQ"
GCS_PREFIX = "HQ"

def upload_directory_to_gcs(dry_run=False):
    """Upload all files from HQ directory to GCS bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)
    
    source_path = Path(HQ_DIRECTORY)
    if not source_path.exists():
        print(f"❌ Error: {HQ_DIRECTORY} directory not found!")
        return False
    
    uploaded_count = 0
    skipped_count = 0
    
    print(f"📁 Starting sync from: {source_path}")
    print(f"📦 Target bucket: {BUCKET_NAME}")
    print(f"🎯 Prefix: {GCS_PREFIX}")
    if dry_run:
        print("🔍 DRY RUN MODE - No files will be uploaded\n")
    else:
        print()
    
    for file_path in source_path.rglob("*"):
        if file_path.is_file():
            # Get relative path from source directory
            relative_path = file_path.relative_to(source_path)
            blob_name = f"{GCS_PREFIX}/{relative_path}".replace("\\", "/")
            
            # Create blob
            blob = bucket.blob(blob_name)
            
            # Check if file needs updating (compare modification time)
            needs_upload = True
            if blob.exists():
                blob.reload()
                local_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                gcs_mtime = blob.updated.replace(tzinfo=None)
                
                if local_mtime <= gcs_mtime:
                    needs_upload = False
                    skipped_count += 1
                    print(f"⏭️  Skipped (unchanged): {blob_name}")
            
            if needs_upload:
                if dry_run:
                    print(f"📤 Would upload: {blob_name}")
                    uploaded_count += 1
                else:
                    try:
                        blob.upload_from_filename(str(file_path))
                        uploaded_count += 1
                        print(f"✅ Uploaded: {blob_name}")
                    except Exception as e:
                        print(f"❌ Failed to upload {file_path}: {e}")
    
    print(f"\n📊 Sync Summary:")
    print(f"   ✅ Uploaded: {uploaded_count} files")
    print(f"   ⏭️  Skipped: {skipped_count} files (unchanged)")
    print(f"   📍 GCS path: gs://{BUCKET_NAME}/{GCS_PREFIX}/")
    
    return uploaded_count > 0

def trigger_reindex():
    """Trigger re-import in Vertex AI Search data store."""
    print(f"\n🔄 Triggering re-index for data store: {DATA_STORE_ID}")
    
    try:
        # Note: Vertex AI Search automatically re-indexes on a schedule
        # For immediate re-indexing, you would need to create a new import operation
        # This requires additional setup and is typically not needed for small updates
        
        print("ℹ️  Note: Vertex AI Search will automatically re-index within 24 hours.")
        print("   For immediate re-indexing, use the Cloud Console to create a new import job.")
        print(f"   URL: https://console.cloud.google.com/gen-app-builder/data-stores/{DATA_STORE_ID}?project={PROJECT_ID}")
        
        return True
    except Exception as e:
        print(f"❌ Re-index trigger failed: {e}")
        return False

def main():
    """Main sync workflow."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Sync HQ directory to GCS and trigger Vertex AI Search re-index")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be uploaded without actually uploading")
    parser.add_argument("--no-reindex", action="store_true", help="Skip re-index trigger")
    args = parser.parse_args()
    
    print("=" * 60)
    print("  HQ → GCS Sync Tool")
    print("=" * 60)
    print()
    
    # Upload files
    files_uploaded = upload_directory_to_gcs(dry_run=args.dry_run)
    
    # Trigger re-index if files were uploaded
    if files_uploaded and not args.no_reindex and not args.dry_run:
        trigger_reindex()
    elif args.dry_run:
        print("\n🔍 Dry run complete. Use without --dry-run to perform actual sync.")
    
    print("\n✅ Sync workflow complete!")

if __name__ == "__main__":
    main()
