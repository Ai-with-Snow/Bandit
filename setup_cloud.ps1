# Set Google Cloud environment variables for Bandit
$env:GOOGLE_CLOUD_PROJECT = "project-5f169828-6f8d-450b-923"
$env:GOOGLE_CLOUD_REGION = "us-central1"
$env:REASONING_ENGINE_ID = "6087067895181869056"
$env:VERTEX_AI_SEARCH_DATA_STORE_ID = "bandit-hq-knowledge_1765072850414"
$env:VERTEX_AI_SEARCH_LOCATION = "global"

Write-Host "Environment configured for Bandit HQ" -ForegroundColor Green
Write-Host "  - Project: $env:GOOGLE_CLOUD_PROJECT" -ForegroundColor Cyan
Write-Host "  - Region: $env:GOOGLE_CLOUD_REGION" -ForegroundColor Cyan
Write-Host "  - Engine ID: $env:REASONING_ENGINE_ID" -ForegroundColor Cyan
Write-Host "  - RAG Data Store: $env:VERTEX_AI_SEARCH_DATA_STORE_ID" -ForegroundColor Cyan
Write-Host ""
Write-Host "You can now run the deployment smoke test:"
Write-Host "   python scripts/deploy.py"
