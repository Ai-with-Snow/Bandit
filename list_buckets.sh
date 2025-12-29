#!/bin/bash
export GOOGLE_APPLICATION_CREDENTIALS="/mnt/c/Users/Goddexx Snow/AppData/Roaming/gcloud/application_default_credentials.json"
export GOOGLE_CLOUD_PROJECT="bandit-ai-461718"

cd "/mnt/c/Users/Goddexx Snow/Documents/bandit"

# List buckets
echo "Listing GCS buckets..."
python3 -c "
from google.cloud import storage
client = storage.Client()
buckets = list(client.list_buckets())
print(f'Found {len(buckets)} buckets:')
for b in buckets:
    print(f'  - {b.name}')
"
