@echo off
REM Quick test script for Bandit RAG functionality

REM Load environment
call setup_cloud.ps1

REM Launch Bandit CLI with RAG ready
echo.
echo ========================================
echo   Bandit CLI with RAG Testing
echo ========================================
echo.
echo Available commands:
echo   /rag ^<query^>    - Search HQ knowledge base
echo   /search ^<query^> - Web search
echo   exit            - Quit
echo.
echo Try: /rag what are Bandit's core capabilities?
echo.

py -3.12 scripts/bandit_cli.py --project project-5f169828-6f8d-450b-923 --location global --engine-id 6087067895181869056
