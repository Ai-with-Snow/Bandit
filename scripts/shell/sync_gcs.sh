#!/bin/bash
export GOOGLE_APPLICATION_CREDENTIALS="/mnt/c/Users/Goddexx Snow/AppData/Roaming/gcloud/application_default_credentials.json"
export GOOGLE_CLOUD_PROJECT="project-5f169828-6f8d-450b-923"

cd "/mnt/c/Users/Goddexx Snow/Documents/bandit"

echo "🔄 Syncing HQ to GCS..."
python3 sync_hq_gcs.py
