"""Upload HQ markdown files to Google Cloud Storage for Vertex AI Search."""

import os
from pathlib import Path
from google.cloud import storage

def upload_directory_to_gcs(
    bucket_name: str,
    source_directory: str,
    destination_blob_prefix: str = "HQ"
):
    """Upload all files from a directory to GCS bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    
    source_path = Path(source_directory)
    uploaded_count = 0
    
    print(f"📁 Starting upload from: {source_path}")
    print(f"📦 Target bucket: {bucket_name}")
    print(f"🎯 Prefix: {destination_blob_prefix}\n")
    
    for file_path in source_path.rglob("*"):
        if file_path.is_file():
            # Get relative path from source directory
            relative_path = file_path.relative_to(source_path)
            blob_name = f"{destination_blob_prefix}/{relative_path}".replace("\\", "/")
            
            # Create blob and upload
            blob = bucket.blob(blob_name)
            
            try:
                blob.upload_from_filename(str(file_path))
                uploaded_count += 1
                print(f"✅ Uploaded: {blob_name}")
            except Exception as e:
                print(f"❌ Failed to upload {file_path}: {e}")
    
    print(f"\n🎉 Upload complete! {uploaded_count} files uploaded.")
    print(f"📍 GCS path: gs://{bucket_name}/{destination_blob_prefix}/")

if __name__ == "__main__":
    BUCKET_NAME = "bandit-hq-knowledge-bucket"
    HQ_DIRECTORY = "HQ"
    
    if not Path(HQ_DIRECTORY).exists():
        print(f"❌ Error: {HQ_DIRECTORY} directory not found!")
        exit(1)
    
    upload_directory_to_gcs(BUCKET_NAME, HQ_DIRECTORY)
