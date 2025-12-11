@echo off
REM Wrapper to launch the Bandit CLI with the correct Python environment
REM Usage: bandit.bat [optional args]
@echo off
setlocal

if "%1"=="mobile" (
    echo Starting Bandit Proxy for Mobile App...
    call .venv\Scripts\python.exe proxy_server.py
    goto :eof
)

if "%1"=="council" (
    echo Starting Council Cycle...
    call .venv\Scripts\python.exe scripts/run_council_cycle.py
    goto :eof
)

if "%1"=="watchdog" (
    echo Starting Council Watchdog...
    call .venv\Scripts\python.exe scripts/council_watchdog.py
    goto :eof
)

echo Starting Bandit CLI...
call .venv\Scripts\python.exe scripts/bandit_cli.py %*
