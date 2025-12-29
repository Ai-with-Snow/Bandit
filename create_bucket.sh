#!/bin/bash
export GOOGLE_APPLICATION_CREDENTIALS="/mnt/c/Users/Goddexx Snow/AppData/Roaming/gcloud/application_default_credentials.json"
export GOOGLE_CLOUD_PROJECT="project-5f169828-6f8d-450b-923"

cd "/mnt/c/Users/Goddexx Snow/Documents/bandit"

echo "Creating bucket bandit-hq-docs..."
python3 << 'EOF'
from google.cloud import storage

BUCKET_NAME = "bandit-hq-docs"

client = storage.Client()

# Check if bucket exists
try:
    bucket = client.get_bucket(BUCKET_NAME)
    print(f"Bucket {BUCKET_NAME} already exists")
except:
    print(f"Creating bucket {BUCKET_NAME}...")
    bucket = client.create_bucket(BUCKET_NAME, location="us-central1")
    print(f"✅ Created bucket {BUCKET_NAME}")
EOF
