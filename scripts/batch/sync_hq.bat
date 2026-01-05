@echo off
REM Quick launcher for HQ sync to GCS

echo.
echo ========================================
echo   HQ Knowledge Base Sync
echo ========================================
echo.

REM Check if dry-run mode
if "%1"=="--dry-run" (
    echo MODE: Dry Run (no uploads)
    py -3.12 scripts/sync_hq_to_gcs.py --dry-run
) else (
    echo MODE: Live Sync
    py -3.12 scripts/sync_hq_to_gcs.py
)

echo.
pause
